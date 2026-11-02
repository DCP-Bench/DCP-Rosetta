import json, time, sys
sys.argv = sys.argv
exec(open("/p/p12_ft06.py").read().split("run(\"ft06 ints")[0])
for th in (1, 2, 4, 0):
    run(f"ft06 intervals+lists nb_threads={th}", intervals_lists, tl=30, threads=th)
