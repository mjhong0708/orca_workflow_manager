#!/bin/bash

#SBATCH -J {{ job_name }}
#SBATCH -e stderr-%j.log
#SBATCH -o stdout-%j.log    # output and error file name
#SBATCH -p {{ partition }}
#SBATCH -N 1
#SBATCH -n {{ n_tasks }}

module purge
module add ORCA/5.0.3
export RSH_COMMAND="/usr/bin/ssh -x"
export scratchlocation=/scratch

orcadir="/TGM/Apps/ORCA/5.0.3/bin"
job=${SLURM_JOB_NAME}
job=$(echo ${job%%.*})

if [ ! -d $scratchlocation/$USER ]
then
mkdir -p $scratchlocation/$USER
fi
tdir=$(mktemp -d $scratchlocation/$USER/orcajob__$SLURM_JOB_ID-XXXX)

cp  $SLURM_SUBMIT_DIR/*.inp $tdir/
cp  $SLURM_SUBMIT_DIR/*.gbw $tdir/
cp  $SLURM_SUBMIT_DIR/*.xyz $tdir/

cd $tdir
echo $SLURM_NODELIST > $tdir/$job.nodes
echo "Job execution start: $(date)" >>  $SLURM_SUBMIT_DIR/$job.log
echo "Shared library path: $LD_LIBRARY_PATH" >>  $SLURM_SUBMIT_DIR/$job.log
echo "Slurm Job ID is: ${SLURM_JOB_ID}" >>  $SLURM_SUBMIT_DIR/$job.log
echo "Slurm Job name is: ${SLURM_JOB_NAME}" >>  $SLURM_SUBMIT_DIR/$job.log
echo $SLURM_NODELIST >> $SLURM_SUBMIT_DIR/$job.log

$orcadir/orca $tdir/orca.inp > $SLURM_SUBMIT_DIR/orca.out
cp $tdir/* $SLURM_SUBMIT_DIR

cd $SLURM_SUBMIT_DIR
rm -rf $tdir

{% if db is not none %}
save_db --db {{ db }} --job-type orca
{% endif %}
