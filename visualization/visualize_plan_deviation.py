from task import Task
from config import *
import matplotlib.pyplot as plt
import math

def visualize_plan_deviation(n=100000):
    # generate list of tasks
    tasks = []
    for i in range(n):
        tasks.append(Task(TASK_MAX_LEN, 0, 0))

    # sort into buckets
    bucket_size = 10000
    counter = dict()
    min_bucket, max_bucket = math.inf, -math.inf
    for t in tasks:
        # find bucket
        distance_to_plan = t.length_plan - t.length_real
        bucket_num = int(distance_to_plan / bucket_size)
        # insert in bucket
        if bucket_num in counter:
            counter[bucket_num] += 1
        else:
            counter[bucket_num] = 1
        if bucket_num < min_bucket:
            min_bucket = bucket_num
        if bucket_num > max_bucket:
            max_bucket = bucket_num

    counter[0] /= 2
    buckets = list(counter)
    buckets.sort()

    plt.hist([(x.length_plan - x.length_real)/INS_PER_TICK for x in tasks], bins=1000)
    plt.ylabel('Occurances')
    plt.xlabel('Plan deviation worth in timer ticks')
    caption = f'task length is {int(TASK_MAX_LEN/INS_PER_TICK)} timer ticks'
    plt.title(caption)
    plt.savefig('../pics/plan_dev.png', dpi=300)


if __name__ == '__main__':
    visualize_plan_deviation()
