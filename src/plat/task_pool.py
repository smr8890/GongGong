import asyncio

from tqdm import tqdm


class AsyncTask:
    """
    异步任务
    """

    def __init__(self, queue: asyncio.Queue, on_done=None):
        self.queue = queue
        self.on_done = on_done or (lambda: None)

    async def run(self):
        while True:
            task = await self.queue.get()
            res = await task
            self.queue.task_done()
            self.on_done()


class AsyncTaskPool:
    """
    异步任务池
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks = asyncio.Queue()

    def add_task(self, task):
        self.tasks.put_nowait(task)

    def run(self, verbose=False):
        asyncio.run(self._run(verbose=verbose))

    async def _run(self, verbose=False):
        on_done = None
        if verbose:
            # 查看精度
            t = tqdm(total=self.tasks.qsize())
            on_done = lambda: t.update(1)
        workers = [asyncio.create_task(
            AsyncTask(queue=self.tasks, on_done=on_done).run()
        ) for _ in range(self.max_workers)]
        await self.tasks.join()
        for worker in workers:
            worker.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
