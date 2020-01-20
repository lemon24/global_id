## Setup

I ran the benchmarks on a [t3a.nano instance](https://aws.amazon.com/ec2/instance-types/t3/) 
with 2 virtual CPUs, on Ubuntu 18.04.

I ran the benchmarks with both CPython (the reference Python implementation) 
and PyPy (a JITed Python implementation).


## Results

The simple benchmark consists of requesting ids as fast as possible in the same 
process.

Both interpreters managed to exhaust the ids that can be generated 
in a second (~131K); after that, PyPy got significantly more OutOfIds errors,
hinting that it would generate more ids if maximum sequence would be increased.

The UDP benchmark consists of multiple server processes serving IDs for a
node, and multiple client processes requesting IDs. The server processes
were bound to the same port; the sockets had the SO_REUSEPORT option set,
so the kernel would balance the load (see the `global_id_udp.run_server()` 
and the `benchmark_udp` module docstrings for details).

For both interpreters, maximum performance was achieved with 1 server
process / CPU (i.e. 2 server processes).

On CPython, the server *did not* manage to generate 100K ids/second.
I suspect this is because it can't send/receive packets fast enough,
although I did manage to reach 100K requests/second with a simple echo server,
so the code itself being slow is probably an issue too.

On PyPy, the server *did* generate over 100K ids/second (~110K).

I think on both interpreters the UDP server would be able to generate
more ids if it had more cores (until it reaches some kernel bottleneck).

I noticed that the PyPy request rate dips sometimes for a few seconds.
I suspect this is because the server processes end up on the same CPU,
but I did not confirm it yet; if true, it can be fixed by pinning the
processes to a specific CPU with [taskset](https://linux.die.net/man/1/taskset)
or [os.sched_setaffinity](https://docs.python.org/3/library/os.html#os.sched_setaffinity).


## Details

### Instance details

```
$ echo $( curl http://169.254.169.254/latest/meta-data/instance-type -s )
t3a.nano
$ cat /proc/cpuinfo | grep -E '^processor' -c
2
$ cat /proc/cpuinfo | grep -E '^(vendor_id|model name|cpu MHz|cache size)' | sort | uniq
cache size	: 512 KB
cpu MHz		: 2199.522
model name	: AMD EPYC 7571
vendor_id	: AuthenticAMD
$ lsb_release -a
No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 18.04.2 LTS
Release:	18.04
Codename:	bionic
```

### Simple benchmark (CPython)

```
$ timeout 10 python3 benchmark_simple.py 
ok: 131072, error: 256629
ok: 131072, error: 272435
ok: 131072, error: 266913
ok: 131072, error: 271759
ok: 131072, error: 272075
ok: 131072, error: 274026
ok: 131072, error: 276719
ok: 131072, error: 279345
ok: 131072, error: 274917
```

### Simple benchmark (PyPy)

```
$ rm -r __pycache__/
$ timeout 10 pypy3 benchmark_simple.py 
ok: 131072, error: 3740912
ok: 131072, error: 4003500
ok: 131072, error: 4039913
ok: 131072, error: 4026500
ok: 131072, error: 4008353
ok: 131072, error: 4015308
ok: 131072, error: 4033250
```

### UDP benchmark (CPython)

```
$ timeout 10 python3 benchmark_udp.py 1
ok: 12409, error: 3159; ok: [12409], error: [3159]
ok: 15299, error: 0; ok: [15299], error: [0]
ok: 15076, error: 0; ok: [15076], error: [0]
ok: 14949, error: 0; ok: [14949], error: [0]
ok: 14815, error: 0; ok: [14815], error: [0]
ok: 14876, error: 0; ok: [14876], error: [0]
ok: 15163, error: 0; ok: [15163], error: [0]
ok: 15065, error: 0; ok: [15065], error: [0]
ok: 14934, error: 0; ok: [14934], error: [0]
```

```
$ timeout 10 python3 benchmark_udp.py 2
ok: 41794, error: 19232; ok: [20884, 20910], error: [9623, 9609]
ok: 55493, error: 0; ok: [28085, 27408], error: [0, 0]
ok: 35303, error: 0; ok: [15387, 19916], error: [0, 0]
ok: 51876, error: 0; ok: [25931, 25945], error: [0, 0]
ok: 59508, error: 0; ok: [29756, 29752], error: [0, 0]
ok: 59864, error: 0; ok: [29934, 29930], error: [0, 0]
ok: 59976, error: 0; ok: [29989, 29987], error: [0, 0]
ok: 59570, error: 0; ok: [29786, 29784], error: [0, 0]
ok: 59505, error: 0; ok: [29759, 29746], error: [0, 0]
```

```
$ timeout 10 python3 benchmark_udp.py 4
ok: 34297, error: 24738; ok: [4446, 13143, 4834, 11874], error: [3679, 7242, 3510, 10307]
ok: 55238, error: 0; ok: [8346, 19450, 9370, 18072], error: [0, 0, 0, 0]
ok: 54915, error: 0; ok: [11712, 17196, 9378, 16629], error: [0, 0, 0, 0]
ok: 56079, error: 0; ok: [7773, 20795, 7678, 19833], error: [0, 0, 0, 0]
ok: 55051, error: 0; ok: [9728, 15203, 7664, 22456], error: [0, 0, 0, 0]
ok: 50884, error: 0; ok: [8853, 17216, 10047, 14768], error: [0, 0, 0, 0]
ok: 53109, error: 0; ok: [9728, 15208, 9722, 18451], error: [0, 0, 0, 0]
ok: 57058, error: 0; ok: [8883, 18870, 8716, 20589], error: [0, 0, 0, 0]
ok: 53491, error: 0; ok: [9739, 18140, 9535, 16077], error: [0, 0, 0, 0]
```

### UDP benchmark (PyPy)

```
$ rm -r __pycache__/
$ timeout 10 pypy3 benchmark_udp.py 1
ok: 11172, error: 6546; ok: [11172], error: [6546]
ok: 21411, error: 0; ok: [21411], error: [0]
ok: 21131, error: 0; ok: [21131], error: [0]
ok: 21128, error: 0; ok: [21128], error: [0]
ok: 21164, error: 0; ok: [21164], error: [0]
ok: 20974, error: 0; ok: [20974], error: [0]
ok: 21497, error: 0; ok: [21497], error: [0]
```

```
$ rm -r __pycache__/
$ timeout 20 pypy3 benchmark_udp.py 2
ok: 100373, error: 1674; ok: [50183, 50190], error: [890, 784]
ok: 113960, error: 0; ok: [56952, 57008], error: [0, 0]
ok: 113819, error: 0; ok: [56905, 56914], error: [0, 0]
ok: 114609, error: 0; ok: [57281, 57328], error: [0, 0]
ok: 114644, error: 0; ok: [57313, 57331], error: [0, 0]
ok: 83145, error: 0; ok: [47786, 35359], error: [0, 0]
ok: 59269, error: 0; ok: [32349, 26920], error: [0, 0]
ok: 109367, error: 0; ok: [55029, 54338], error: [0, 0]
ok: 104835, error: 0; ok: [52394, 52441], error: [0, 0]
ok: 113851, error: 0; ok: [56917, 56934], error: [0, 0]
ok: 114157, error: 0; ok: [57062, 57095], error: [0, 0]
ok: 114716, error: 0; ok: [57346, 57370], error: [0, 0]
ok: 113964, error: 0; ok: [56972, 56992], error: [0, 0]
ok: 114413, error: 0; ok: [57173, 57240], error: [0, 0]
ok: 114907, error: 0; ok: [57423, 57484], error: [0, 0]
ok: 114126, error: 0; ok: [57046, 57080], error: [0, 0]
ok: 114159, error: 0; ok: [57062, 57097], error: [0, 0]
ok: 111910, error: 0; ok: [56389, 55521], error: [0, 0]
```

```
$ rm -r __pycache__/
$ timeout 20 pypy3 benchmark_udp.py 4
ok: 46975, error: 13119; ok: [11699, 11783, 11818, 11675], error: [2417, 2052, 6601, 2049]
ok: 102659, error: 0; ok: [25306, 25640, 25796, 25917], error: [0, 0, 0, 0]
ok: 108238, error: 0; ok: [26996, 27073, 27043, 27126], error: [0, 0, 0, 0]
ok: 107374, error: 0; ok: [26804, 26856, 26819, 26895], error: [0, 0, 0, 0]
ok: 107522, error: 0; ok: [26851, 26912, 26840, 26919], error: [0, 0, 0, 0]
ok: 107623, error: 0; ok: [26858, 26910, 26903, 26952], error: [0, 0, 0, 0]
ok: 106745, error: 0; ok: [26602, 26710, 26686, 26747], error: [0, 0, 0, 0]
ok: 106816, error: 0; ok: [26570, 26789, 26785, 26672], error: [0, 0, 0, 0]
ok: 106649, error: 0; ok: [26588, 26680, 26675, 26706], error: [0, 0, 0, 0]
ok: 99933, error: 0; ok: [23631, 26339, 26251, 23712], error: [0, 0, 0, 0]
ok: 105233, error: 0; ok: [26261, 26334, 26267, 26371], error: [0, 0, 0, 0]
ok: 105142, error: 0; ok: [26242, 26313, 26261, 26326], error: [0, 0, 0, 0]
ok: 105844, error: 0; ok: [26216, 26707, 26670, 26251], error: [0, 0, 0, 0]
ok: 107011, error: 0; ok: [26695, 26802, 26715, 26799], error: [0, 0, 0, 0]
ok: 106929, error: 0; ok: [26634, 26793, 26707, 26795], error: [0, 0, 0, 0]
ok: 105242, error: 0; ok: [25865, 26704, 26663, 26010], error: [0, 0, 0, 0]
ok: 106579, error: 0; ok: [26703, 26687, 26692, 26497], error: [0, 0, 0, 0]
```
