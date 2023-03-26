from multiprocessing import Pool, cpu_count

class ServerPool:
    """
    Pool of processes
    """
    def __init__(self, pool_size: int = cpu_count()) -> None:
        self._pool_size = pool_size if pool_size <= cpu_count() else cpu_count()
        self._pool = None

    def start(self):
        self._pool = Pool(processes=self._pool_size)

    def apply(self, callable):
        return self._pool.apply_async(func=callable)

    def stop(self):
        # `close` actually must go before join as close prevents any more tasks from being submitted into the pool
        # and waits for them to finish
        self._pool.close()
        # join actually releases the resources held by the pool
        self._pool.join()