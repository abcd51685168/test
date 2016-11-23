# Spark Application - execute with spark-submit

# Imports
from pyspark import SparkConf, SparkContext
from operator import add

# Module Constants
APP_NAME = "My Spark Application"


# Closure Functions

def tokenize(text):
    return text.split()


# Main functionality
def main(sc):
    text = sc.textFile("/tmp/test.txt")
    words = text.flatMap(tokenize)
    wc = words.map(lambda x: (x, 1))
    counts = wc.reduceByKey(add)
    map_counts = counts.map(lambda (x, y): (y, x))
    map_sorted_counts = map_counts.sortByKey(False)
    sorted_counts = map_sorted_counts.map(lambda (x, y): (y, x))
    sorted_counts.saveAsTextFile("wc")
    top5 = sorted_counts.take(5)
    for i in top5:
        print i


if __name__ == "__main__":
    # Configure Spark
    conf = SparkConf().setAppName(APP_NAME)
    conf = conf.setMaster("local[*]")
    sc = SparkContext(conf=conf)

    # Execute Main functionality
    main(sc)
