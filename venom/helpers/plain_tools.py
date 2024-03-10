""" Tools developed by plain-ub dev """
import asyncio
from asyncio.subprocess import Process


async def run_shell_cmd(cmd: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    return stdout.decode("utf-8")


class AsyncShell:

    def __init__(self, process: asyncio.subprocess.Process):
        self.process: asyncio.subprocess.Process = process
        self.full_std = ""
        self.last_line = ""
        self.is_done = False
        self._task: asyncio.Task | None = None

    async def read_output(self):
        async for line in self.process.stdout:
            decoded_line = line.decode("utf-8")
            self.full_std += decoded_line
            self.last_line = decoded_line
        self.is_done = True
        await self.process.wait()

    async def get_output(self):
        while not self.is_done:
            yield self.full_std if len(self.full_std) < 4000 else self.last_line
            await asyncio.sleep(0)

    def cancel(self):
        if not self.is_done:
            self.process.kill()
            self._task.cancel()

    @classmethod
    async def run_cmd(cls, cmd: str, name: str = "AsyncShell") -> "AsyncShell":
        sub_process = cls(process=await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT))
        sub_process._task = asyncio.create_task(sub_process.read_output(), name=name)
        await asyncio.sleep(0.5)
        return sub_process
