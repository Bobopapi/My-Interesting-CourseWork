from tripsage.pipelines.run_crawl import run as run_crawl
from tripsage.pipelines.run_silver import run as run_silver
from tripsage.pipelines.run_analytics import run as run_analytics


def run():
    run_crawl()
    run_silver()
    run_analytics()


if __name__ == "__main__":
    run()
