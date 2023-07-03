# RH15D

<https://tiagopereira.space/ast5210/>

<!-- MarkdownTOC -->

- [Configuration](#configuration)
    - [Mac OS](#mac-os)
    - [GNU/Linux](#gnulinux)
- [Build](#build)
- [Run](#run)

<!-- /MarkdownTOC -->

## Configuration

Clone repository:

``` sh
$ git clone git@github.com:ITA-Solar/rh.git
```

### Mac OS

``` sh
$ brew install open-mpi
$ brew install hdf5-mpi
```

Edit `Makefile.config`:

```
CC       = mpicc
CFLAGS   = -O2 -DHAVE_F90 -Wformat

F90C     = gfortran
F90FLAGS = -O2

LD       = mpicc
LDFLAGS  =

AR       = ar
ARFLAGS  = rs
RANLIB   = ranlib

HDF5_DIR = /usr/local/opt/hdf5-mpi

OS = $(shell uname -s)
```

### GNU/Linux

``` sh
$ sudo apt install libopenmpi-dev openmpi-bin
$ sudo apt install libntirpc-dev
$ sudo apt install libhdf5-mpi-dev
```

It's important to install exactly `libhdf5-mpi-dev` and not `libhdf5-dev`, because the latter isn't parallel, while the former is, and RH requires the parallel one. If you won't install the parallel variant, you'll get the following linking errors trying to build RH15D tools:

```
/usr/bin/ld: hdf5atmos.o: in function `init_hdf5_atmos':
hdf5atmos.c:(.text+0x72): undefined reference to `H5Pset_fapl_mpio'
/usr/bin/ld: writeAux_p.o: in function `init_aux_new':
writeAux_p.c:(.text+0x7c): undefined reference to `H5Pset_fapl_mpio'
/usr/bin/ld: writeAux_p.o: in function `init_aux_existing':
writeAux_p.c:(.text+0x22a2): undefined reference to `H5Pset_fapl_mpio'
/usr/bin/ld: writeRay.o: in function `init_hdf5_ray_new':
writeRay.c:(.text+0x7f): undefined reference to `H5Pset_fapl_mpio'
...
```

Edit `Makefile.config`:

```
CC       = mpicc
CFLAGS   = -O2 -DHAVE_F90 -Wformat -I/usr/include/tirpc

F90C     = gfortran
F90FLAGS = -O2

LD       = mpicc
LDFLAGS  =

AR       = ar
ARFLAGS  = rs
RANLIB   = ranlib

# on Ubuntu HDF5 package in installed into /usr, not /usr/local, but most importantly
# it has a different structure, so you'll need to make adjustments in ./rh15d/Makefile instead
#HDF5_DIR = /usr/local

# The OS variable should have the operative system name
# If the command below is unavailable, please edit manually
OS = $(shell uname -s)
```

Edit `./rh15d/Makefile`:

```
include ../Makefile.config

HDF5_INCLUDE_DIR=/usr/include/hdf5/openmpi
HDF5_LIB_DIR=/usr/lib/x86_64-linux-gnu/hdf5/openmpi

# Try to get git revision, set preprocessor macros if successful
REV=$(shell git describe --always)
ifeq ($(REV), )
    CFLAGS += -I../ -I$(HDF5_INCLUDE_DIR)
else
    REV = $(shell git log -1 --pretty=format:"%h  %an  %ai")
    CFLAGS += -I../ -I$(HDF5_INCLUDE_DIR) -D'REV_ID="$(REV)"'
endif

LDFLAGS += -L../ -L$(HDF5_LIB_DIR) -lrh -lrh_f90 -lhdf5 -lhdf5_hl -lm -lpthread -ltirpc
```

So it's `HDF5_INCLUDE_DIR` and `HDF5_LIB_DIR` variables and their use in `-I` and `-L` flags. Also note the linkage to `-ltirpc`, because without it you'll get these errors trying to build RH15D tools:

```
/usr/bin/ld: writeatom_xdr.c:(.text+0x449): undefined reference to `xdr_double'
/usr/bin/ld: writeatom_xdr.c:(.text+0x491): undefined reference to `xdr_enum'
/usr/bin/ld: writeatom_xdr.c:(.text+0x4af): undefined reference to `xdr_int'
/usr/bin/ld: writeatom_xdr.c:(.text+0x4de): undefined reference to `xdr_double'
/usr/bin/ld: writeatom_xdr.c:(.text+0x578): undefined reference to `xdr_vector'
/usr/bin/ld: ..//librh.a(writeatom_xdr.o): in function `writeAtom':
writeatom_xdr.c:(.text+0x643): undefined reference to `xdrstdio_create'
/usr/bin/ld: ..//librh.a(writeatom_xdr.o): in function `xdr_adamp':
writeatom_xdr.c:(.text+0x760): undefined reference to `xdr_double'
/usr/bin/ld: writeatom_xdr.c:(.text+0x795): undefined reference to `xdr_vector'
...
```

## Build

Main libraries:

``` sh
$ make -j$(nproc --all)
```

Executables:

``` sh
$ cd rh15d
$ make -j$(nproc --all)
```

You should get the following binaries:

- `rh15d_lteray`
- `rh15d_ray`
- `rh15d_ray_pool`

## Run

You can test it by running the following:

``` sh
$ cd run_example
$ mpiexec -np 4 ../rh15d_ray_pool
```

Results will be written to `output` folder.
