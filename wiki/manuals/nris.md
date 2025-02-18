# NRIS

Norwegian Research Infrastructure Services: <https://documentation.sigma2.no/index.html>.

<!-- MarkdownTOC -->

- [Accessing machines](#accessing-machines)
    - [Nodes](#nodes)
    - [Quotas](#quotas)
- [Running jobs](#running-jobs)
    - [Interactive](#interactive)
    - [Queued](#queued)
        - [Job types](#job-types)
- [Installing software](#installing-software)
    - [Loading modules](#loading-modules)
    - [Using EasyBuild](#using-easybuild)
    - [Building from sources](#building-from-sources)

<!-- /MarkdownTOC -->

## Accessing machines

Those are all GNU/Linux servers, so you can just connect to them via SSH/SFTP as usual. At first you can use login/password, which you were granted, but it's better to switch to SSH keys after that. Unfortunately, it doesn't seem possible to disable password authentication and keep only SSH keys authentication.

Machines/servers:

- [Betzy](https://documentation.sigma2.no/hpc_machines/betzy.html#betzy) - `betzy.sigma2.no`
- [Fram](https://documentation.sigma2.no/hpc_machines/fram.html#fram) - `fram.sigma2.no` 
- [Saga](https://documentation.sigma2.no/hpc_machines/saga.html#saga) - `saga.sigma2.no`
- [NIRD](https://documentation.sigma2.no/files_storage/nird_lmd.html#nird) - `login.nird.sigma2.no`

Here's how your local SSH config would look like:

``` ini
Host betzy
HostName betzy.sigma2.no
SetEnv LC_CTYPE=C # there seem to be some problems with locale there
IdentityFile ~/.ssh/nris # or whichever you created
User USERNAME-THAT-YOU-WERE-GRANTED
```

### Nodes

Cluster has login nodes and compute notes.

Login nodes are just entry points to the cluster and **it is not allowed** to run heavy tasks on those, even if you just need to compile some tool. When you run some tasks which might occupy several CPU cores, do set an explicit limit to those, otherwise by default they most likely will occupy all the available cores.

Compute nodes are where you are supposed to be running your calculations, compilations and any other heavy tasks/jobs.

### Quotas

CPU hours:

``` sh
$ cost --details
Allocation period 2023.2 (2023-10-01 - 2024-04-01)
Accounting updated 2024-01-27 11:14:05
============================================
Account                            Cpu hours
--------------------------------------------
PROJECT-ID-HERE  Quota (pri)       500000.00
PROJECT-ID-HERE  Quota (nonpri)         0.00
PROJECT-ID-HERE  Used              358864.79
PROJECT-ID-HERE  Running             9218.57
PROJECT-ID-HERE  Pending                0.00
PROJECT-ID-HERE  Available         131916.65
--------------------------------------------
Account          User         Used cpu hours
--------------------------------------------
PROJECT-ID-HERE  someone1          355442.28
PROJECT-ID-HERE  someone2            4645.47
PROJECT-ID-HERE  someone3             314.88
============================================
```

Disk space:

```
$ dusage
                        path    space used    quota (s)    quota (h)    files    quota (s)    quota (h)
----------------------------  ------------  -----------  -----------  -------  -----------  -----------
      /cluster/home/USERNAME      12.0 KiB     20.0 GiB     30.0 GiB        3      100 000      110 000
/cluster/projects/PROJECT-ID     417.3 GiB      1.0 TiB      1.0 TiB  882 855    1 000 000    1 000 000
```

## Running jobs

First you need to choose on which server you'll be running your jobs. That depends on the jobs requirements for hardware, and for example jobs with a lot of parallel computing are probably better to be run on `betzy`, while singe-threaded but hungry for RAM jobs are better to be run on `saga`.

### Interactive

To run/execute computational tasks right here right now you can start an [interactive job](https://documentation.sigma2.no/jobs/interactive_jobs.html), for example on `betzy`:

``` sh
$ salloc --nodes=1 --cpus-per-task=8 --time=00:59:00 --qos=devel --account=YOUR-PROJECT-ID
```

or on `saga`:

``` sh
$ salloc --ntasks=1 --cpus-per-task=8 --mem=8G --time=00:59:00 --qos=devel --account=YOUR-PROJECT-ID
```

The `YOUR-PROJECT-ID` value you can get from [quotas](#quotas) output. Or you can list all your projects:

``` sh
$ projects
ololo1
ololo2
ololo3
```

If the task you'd like to run that way is a rather long one, first start a [screen](https://github.com/retifrav/scraps/blob/master/_linux/index.md#screen) session on the login node and from there start the interactive job. Important to note here that there is more than one login node, and so to resume your screen session later you'll need to know on this login node you started it and connect to exactly that particular node.

### Queued

To submit a job to the queue, you need to write a [job script](https://documentation.sigma2.no/jobs/job_scripts.html). Be aware that jobs can be quite expensive in billing hours, especially of you'll request 4 nodes with many CPUs, but in fact your job would only use a single CPU on one node, leaving you with a lot of wasted resources which you need to pay for.

So for example, here's a single-process job for `betzy`:

``` sh
$ mkdir -p ~/jobs/outputs
$ nano ~/jobs/some.sh
```
``` sh
#!/bin/bash

# these are not comments, so do not "uncomment" them
#
#SBATCH --account=YOUR-PROJECT-ID
#SBATCH --job-name=some
#SBATCH --partition=accel
#SBATCH --nodes=1 --ntasks=1 --ntasks-per-node=1 --cpus-per-task=1 --gpus=0
#SBATCH --mem=40G
#SBATCH --time=08:00:00
#SBATCH --output=/cluster/home/YOUR-USERNAME/jobs/outputs/%j.log

set -o errexit # exit the script on any error
set -o nounset # treat any unset variables as an error

# create a new folder for the job
#workingdir=$USERWORK/$SLURM_JOB_ID
workingdir=/cluster/projects/YOUR-PROJECT-ID/YOUR-USERNAME/SOMETHING
mkdir -p $workingdir
cd $workingdir

# what modules were loaded
module list

echo 'Job variables:'
echo ''
echo "- SLURM_JOB_ID: $SLURM_JOB_ID"
echo "- SLURM_JOB_NODELIST: $SLURM_JOB_NODELIST"
echo "- SLURM_NTASKS: $SLURM_NTASKS"
echo "- SLURM_SUBMIT_DIR: $SLURM_SUBMIT_DIR"
echo "- SCRATCH: $SCRATCH"
echo "- OMP_NUM_THREADS: $OMP_NUM_THREADS"
echo ''

# the actual stuff to do

echo "[$(date '+%Y-%m-%d %H:%M:%S')] started"
echo ''

python ./vulcan.py

echo ''
echo "[$(date '+%Y-%m-%d %H:%M:%S')] finished"

# Telegram notification
jq -nc --arg msg "🌌 job #<code>$SLURM_JOB_ID</code> is done" '{"chat_id": "YOUR-TELEGRAM-ID", "text": $msg, "parse_mode": "HTML", "disable_web_page_preview": "true"}' \
    | curl -s -X POST -H "Content-Type: application/json" -d @- \
    https://api.telegram.org/botYOUR-TELEGRAM-BOT-API-TOKEN/sendMessage \
    > /dev/null

echo ''
echo '--- Slurm statistics ---'
```
``` sh
$ chmod +x ~/jobs/some.sh
```

For `saga` the `SBATCH` arguments would be different (*but actually, don't use `saga` for anything, because even though it is cheaper than others, it is also slow as shit*):

``` sh
#SBATCH --account=YOUR-PROJECT-ID
#SBATCH --job-name=some
#SBATCH --cpus-per-task=1
#SBATCH --mem=40G
#SBATCH --time=08:00:00
#SBATCH --output=/cluster/home/YOUR-USERNAME/jobs/outputs/%j.log
```

Obviously, if your job is for parallel processing, then you'll need to increase the tasks/nodes/CPUs values.

Once the script is ready, you can submit it to the queue:

``` sh
$ sbatch ~/jobs/some.sh
Submitted batch job 796687
```

You can find the job in the queue (*if it is still queued*):

``` sh
$ squeue -j 796687
```

or:

``` sh
$ squeue -u YOUR-USERNAME
```

To check its status:

``` sh
$ sstat -j 796687
$ sacct -j 796687
$ scontrol show job 796687

$ seff 796687
Job ID: 796687
Cluster: betzy
User/Group: YOUR-USERNAME/YOUR-USERNAME
State: FAILED (exit code 1)
Nodes: 1
Cores per node: 128
CPU Utilized: 00:00:00
CPU Efficiency: 0.00% of 00:02:08 core-walltime
Job Wall-clock time: 00:00:01
Memory Utilized: 0.00 MB (estimated maximum)
Memory Efficiency: 0.00% of 242.00 GB (242.00 GB/node
```

When it's finished running, the output will be in the `~/jobs/slurm-796687.out` file (*or whichever folder you'll run `sbatch` from?*).

#### Job types

There are different [job types](https://documentation.sigma2.no/jobs/choosing_job_types.html), and if you haven't specified one explicitly, it will default to `normal`. To specify a different type:

``` sh
#SBATCH --qos=preproc
```

or, which depends on a particular server:

``` sh
#SBATCH --partition=accel
```

The point is that different job types have different cost/pricing and different "walltime" limits (*for how long can your job run before it gets killed by scheduler*). So if your tasks are running for longer than 4 days then you'll just have to use the `accel` type (*and set `--gpus=0` if you don't need GPU*), no matter the cost/price; but if your tasks need to run for longer than 7 days, then it isn't clear what one should do in that case.

## Installing software

### Loading modules

First of all, there is a good amount of pre-installed software with fairly recent versions. You just need to activate it with [Lmod](https://lmod.readthedocs.io/en/latest/010_user.html), for example:

``` sh
$ git --version
git version 1.8.3.1

$ module avail git
------------------------------------------------------------------------ /cluster/modulefiles/all -------------------------------------------------------------------------
   git/2.21.0-GCCcore-8.2.0           git/2.28.0-GCCcore-10.2.0-nodocs    git/2.36.0-GCCcore-11.3.0-nodocs    git/2.42.0-GCCcore-13.2.0
   git/2.23.0-GCCcore-8.3.0           git/2.32.0-GCCcore-10.3.0-nodocs    git/2.38.1-GCCcore-12.2.0-nodocs
   git/2.23.0-GCCcore-9.3.0-nodocs    git/2.33.1-GCCcore-11.2.0-nodocs    git/2.41.0-GCCcore-12.3.0-nodocs

$ module whatis git/2.42.0-GCCcore-13.2.0
git/2.42.0-GCCcore-13.2.0                           : Description: Git is a free and open source distributed version control system designed
to handle everything from small to very large projects with speed and efficiency.
git/2.42.0-GCCcore-13.2.0                           : Homepage: https://git-scm.com
git/2.42.0-GCCcore-13.2.0                           : URL: https://git-scm.com

$ module load git/2.42.0-GCCcore-13.2.0

$ git --version
git version 2.42.0
```

To see the list of currently loaded modules:

``` sh
$ module list

Currently Loaded Modules:
  1) StdEnv                          (S)  11) libffi/3.4.4-GCCcore-12.2.0            (H)  21) GCC/12.2.0                            31) zlib/1.2.12-GCCcore-12.2.0    (H)
  2) Ruby/3.0.5-GCCcore-11.3.0            12) ncurses/6.3-GCCcore-12.2.0             (H)  22) numactl/2.0.16-GCCcore-12.2.0    (H)  32) gzip/1.12-GCCcore-12.2.0      (H)
  3) OpenSSL/1.1                     (H)  13) gettext/0.21.1-GCCcore-12.2.0          (H)  23) libpciaccess/0.17-GCCcore-12.2.0 (H)  33) XZ/5.2.7-GCCcore-12.2.0       (H)
  4) expat/2.5.0-GCCcore-13.2.0      (H)  14) PCRE2/10.40-GCCcore-12.2.0             (H)  24) hwloc/2.8.0-GCCcore-12.2.0       (H)  34) lz4/1.9.4-GCCcore-12.2.0      (H)
  5) libiconv/1.17-GCCcore-13.2.0    (H)  15) util-linux/2.38.1-GCCcore-12.2.0       (H)  25) hpcx/2.13.1                           35) zstd/1.5.2-GCCcore-12.2.0     (H)
  6) Perl/5.38.0-GCCcore-13.2.0           16) GLib/2.75.0-GCCcore-12.2.0             (H)  26) OpenMPI/4.1.4-GCC-12.2.0              36) GCCcore/12.2.0
  7) git/2.42.0-GCCcore-13.2.0            17) intel-compilers/2022.1.0                    27) gompi/2022b                           37) bzip2/1.0.8-GCCcore-12.2.0    (H)
  8) libarchive/3.7.2-GCCcore-13.2.0 (H)  18) impi/2021.6.0-intel-compilers-2022.1.0      28) Szip/2.1.1-GCCcore-12.2.0        (H)  38) libxml2/2.10.3-GCCcore-12.2.0 (H)
  9) CMake/3.27.6-GCCcore-13.2.0          19) iimpi/2022a                                 29) HDF5/1.14.0-gompi-2022b               39) netCDF/4.9.0-gompi-2022b
 10) EasyBuild/4.9.0                      20) binutils/2.39-GCCcore-12.2.0           (H)  30) cURL/7.86.0-GCCcore-12.2.0       (H)  40) nano/7.2-GCCcore-12.2.0
```

To save current list:

``` sh
$ module save mine
```

To restore particular list:

``` sh
$ module restore mine
```

You might want to add that last command to your `~/.bashrc`.

### Using EasyBuild

If something isn't available in pre-installed modules, you can install additional ones with [EasyBuild](https://documentation.sigma2.no/software/userinstallsw/easybuild.html) (*don't forget to limit the number of cores with `--parallel`*).

``` sh
$ nano --version
 GNU nano version 2.3.1 (compiled 12:47:08, Jan 26 2014)

$ eb nano-7.2-GCCcore-12.2.0.eb --fetch
$ eb nano-7.2-GCCcore-12.2.0.eb --robot --parallel=10
```

It will be fetched, built and installed into `~/.local/easybuild`. After that you can now activate it as a module:

``` sh
$ module use $HOME/.local/easybuild/modules/all
$ module load nano/7.2-GCCcore-12.2.0

$ nano --version
 GNU nano, version 7.2
```

If you save you modules now, it will for some reason fail to restore that one later. So unload it and re-save the collection:

``` sh
$ module unload nano/7.2-GCCcore-12.2.0
$ module save mine
```

and do the following in your `~/.bashrc` instead:

``` sh
module restore mine # first restore "stable" collection of pre-installed modules
module use $HOME/.local/easybuild/modules/all # then add your own EasyBuild ones
module load nano/7.2-GCCcore-12.2.0 # and then activate them one by one
```

And looks like it will happen with every other executable installed that way. Libraries seem to be fine.

### Building from sources

If the software you need isn't available in EasyBuild either, you can then build it from sources yourself. Just use your `~/.local` as the installation prefix. All the building dependencies can also go there, and so you'll probably want to export some development environment variables in your `~/.bashrc`, such as:

``` sh
export PKG_CONFIG_PATH="$HOME/.local/lib/pkgconfig:$PKG_CONFIG_PATH"
```

Don't forget that building/compilation shouldn't be run on login nodes, you need to start an [interactive job](#interactive) on compute nodes.
