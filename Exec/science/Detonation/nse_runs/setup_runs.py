#!/usr/bin/env python

import os
import shutil
import subprocess
import shlex
from multiprocessing import Pool
import time

# parameters for all methods
CFL = [0.5] #, 0.1]
NZONES = [256, 512] #, 1024, 2048] #, 8192]
DTNUC_E = [1.e200, 1.0, 0.25] #, 0.1]

# simplified SDC parameters
SDC_ITERS = [2]

# true SDC parameters
SDC_QUADRATURE = [0, 1]
SDC_ORDER = [2] #, 4]

# turn on or off the different integrator types
do_strang_runs = 1
do_simple_sdc_runs = 1
do_true_sdc_runs = 1

COMMON_FILES = ["helm_table.dat", "probin-det-x.nse_disabled"] #, "nse19.tbl"]

STRANG_EXEC = "./Castro1d.gnu.ex"
NEEDED_STRANG_FILES = [STRANG_EXEC] + COMMON_FILES

SIMPLE_SDC_EXEC = "./Castro1d.gnu.SMPLSDC.ex"
NEEDED_SIMPLE_SDC_FILES = [SIMPLE_SDC_EXEC] + COMMON_FILES

TRUE_SDC_EXEC = "./Castro1d.gnu.TRUESDC.ex"
NEEDED_TRUE_SDC_FILES = [TRUE_SDC_EXEC] + COMMON_FILES

def setup_runs():

    with open("inputs.template.simple_sdc", "r") as tf:
        simple_sdc_template = tf.readlines()

    with open("inputs.template.true_sdc", "r") as tf:
        true_sdc_template = tf.readlines()

    with open("inputs.template.strang", "r") as tf:
        strang_template = tf.readlines()

    job_list = []

    if do_strang_runs:
        # setup the Strang runs
        for nz in NZONES:
            for dtn in DTNUC_E:
                for c in CFL:

                    # don't do all the CFLs when using the nuc energy dt limiter
                    if dtn < 1.0 and c != CFL[0]:
                        continue

                    # make the output directory
                    odir = "det_strang_cfl{}_dtnuce{}_nzones{}".format(c, dtn, nz)
                    os.mkdir(odir)

                    job_list.append(odir)

                    # dump the metdata file
                    with open("{}/run.meta".format(odir), "w") as meta:
                        meta.write("cfl = {}\n".format(c))
                        meta.write("nzones = {}\n".format(nz))
                        meta.write("integrator = Strang\n")
                        meta.write("dtnuc_e = {}\n".format(dtn))

                    # write the inputs file
                    with open("{}/inputs".format(odir), "w") as inpf:
                        for line in strang_template:
                            inpf.write(line.replace("@@CFL@@", str(c)).replace("@@NZONES@@", str(nz)).replace("@@method@@", "0").replace("@@DTNUC_E@@", str(dtn)))

                    # copy the remaining files
                    for f in NEEDED_STRANG_FILES:
                        shutil.copy(f, odir)

    if do_simple_sdc_runs:
        # setup the simplified SDC runs
        for nz in NZONES:
            for dtn in DTNUC_E:
                for c in CFL:
                    for niter in SDC_ITERS:

                        # don't do all the CFLs when using the nuc energy dt limiter
                        if dtn < 1.0 and c != CFL[0]:
                            continue

                        # make the output directory
                        odir = "det_simple_sdc_iter{}_cfl{}_dtnuce{}_nzones{}".format(niter, c, dtn, nz)
                        os.mkdir(odir)

                        job_list.append(odir)

                        # dump the metdata file
                        with open("{}/run.meta".format(odir), "w") as meta:
                            meta.write("cfl = {}\n".format(c))
                            meta.write("nzones = {}\n".format(nz))
                            meta.write("integrator = simplified-SDC\n")
                            meta.write("niters = {}\n".format(niter))
                            meta.write("dtnuc_e = {}\n".format(dtn))

                        # write the inputs file
                        with open("{}/inputs".format(odir), "w") as inpf:
                            for line in simple_sdc_template:
                                inpf.write(line.replace("@@CFL@@", str(c)).replace("@@NZONES@@", str(nz)).replace("@@SDC_ITERS@@", str(niter)).replace("@@method@@", "3").replace("@@DTNUC_E@@", str(dtn)))

                        # copy the remaining files
                        for f in NEEDED_SIMPLE_SDC_FILES:
                            shutil.copy(f, odir)

    if do_true_sdc_runs:
        # setup the true SDC runs
        for nz in NZONES:
            for dtn in DTNUC_E:
                for c in CFL:
                    for quad in SDC_QUADRATURE:
                        for order in SDC_ORDER:

                            # don't do all the CFLs when using the nuc energy dt limiter
                            if dtn < 1.0 and c != CFL[0]:
                                continue

                            # make the output directory
                            odir = f"det_true_sdc_quad{quad}_order{order}_cfl{c}_dtnuce{dtn}_nzones{nz}"
                            os.mkdir(odir)

                            job_list.append(odir)

                            # dump the metdata file
                            with open(f"{odir}/run.meta", "w") as meta:
                                meta.write(f"cfl = {c}\n")
                                meta.write(f"nzones = {nz}\n")
                                meta.write(f"integrator = true-SDC\n")
                                meta.write(f"quadrature = {quad}\n")
                                meta.write(f"order = {order}\n")
                                meta.write(f"dtnuc_e = {dtn}\n")

                            # write the inputs file
                            with open(f"{odir}/inputs", "w") as inpf:
                                for line in true_sdc_template:
                                    inpf.write(line.replace("@@CFL@@", str(c)).replace("@@NZONES@@", str(nz)).replace("@@SDC_ORDER@@", str(order)).replace("@@SDC_QUADRATURE@@", str(quad)).replace("@@method@@", "2").replace("@@DTNUC_E@@", str(dtn)))

                            # copy the remaining files
                            for f in NEEDED_TRUE_SDC_FILES:
                                shutil.copy(f, odir)

    return job_list

def run(string):
    """run a command and capture the output and return code"""

    # shlex.split will preserve inner quotes
    prog = shlex.split(string)
    p0 = subprocess.Popen(prog, stdin=None, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    stdout0, stderr0 = p0.communicate()
    rc = p0.returncode
    stdout = stdout0.decode('utf-8')

    return stdout, rc


def do_run(name):
    print("running {}...".format(name))

    if "simple_sdc" in name:
        command = f"{SIMPLE_SDC_EXEC} inputs"
    elif "true_sdc" in name:
        command = f"{TRUE_SDC_EXEC} inputs"
    else:
        command = f"{STRANG_EXEC} inputs"

    cwd = os.getcwd()
    os.chdir(name)

    stdout, rc = run(command)

    # add a file indicated the job is complete
    with open("job_status", "w") as jf:
        jf.write("completed\n")

    # output stdout
    with open("stdout", "w") as sout:
        for line in stdout:
            sout.write(line)

    os.chdir(cwd)


if __name__ == "__main__":
    job_list = setup_runs()

    # do the runs
    p = Pool(8)
    p.map(do_run, job_list)
