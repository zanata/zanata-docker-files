FROM centos:@CENTOS_VERSION@
ARG CENTOS_VERSION=@CENTOS_VERSION@
ARG USER=builder
ARG UID=1000
ARG REPO_DIR="/repo"

LABEL build="20171101" \
    description="Build RPMs and create repository for Fedora People repository"

ENV EXTRA_PACKAGES="java-1.8.0-openjdk-devel"

ENTRYPOINT ["/home/builder/build"]

RUN yum install -y createrepo rpm-build rpmdevtools sudo yum-utils $EXTRA_PACKAGES && yum clean all

# create the user and home
RUN useradd -m -G wheel -d /home/builder -u $UID $USER && mkdir -p $REPO_DIR && chown -R $USER $REPO_DIR &&\
    echo "$USER    ALL=(ALL)    NOPASSWD: /usr/bin/yum-builddep" >> /etc/sudoers.d/$USER &&\
    echo "Defaults lecture = never" >> /etc/sudoers.d/lecture

VOLUME $REPO_DIR

USER $USER
WORKDIR /home/builder
RUN echo '%home %(echo $HOME)' >> ~/.rpmmacros &&\
    echo '%_smp_mflags  -j3'  >> ~/.rpmmacros &&\
    echo '%__arch_install_post /usr/lib/rpm/check-rpaths  /usr/lib/rpm/check-buildroot' >> .rpmmacros &&\
    echo '%_topdir /tmp/rpmbuild' >> ~/.rpmmacros &&\
    echo "%_specdir $REPO_DIR" >> ~/.rpmmacros &&\
    echo '%_sourcedir %{_topdir}' >> ~/.rpmmacros &&\
    echo "%_rpmdir $REPO_DIR/epel-${CENTOS_VERSION}" >> ~/.rpmmacros &&\
    echo "%_srcrpmdir $REPO_DIR/epel-${CENTOS_VERSION}/SRPMS" >> ~/.rpmmacros &&\
    echo "%dist .el${CENTOS_VERSION}" >> ~/.rpmmacros &&\
    echo '#!/bin/bash' >> ~/build &&\
    echo 'set -xeu' >> ~/build &&\
    echo 'if [[ $# -eq 0 ]]; then' >> ~/build &&\
    echo '   echo "Usage: $0 [-b] <specfile>"' >> ~/build &&\
    echo '   exit 0' >> ~/build &&\
    echo 'fi' >> ~/build &&\
    echo 'builddep=0' >> ~/build &&\
    echo 'while getopts "b" opt;do' >> ~/build &&\
    echo '    case $opt in' >> ~/build &&\
    echo '        b )' >> ~/build &&\
    echo '           builddep=1' >> ~/build &&\
    echo '           ;;' >> ~/build &&\
    echo '    esac' >> ~/build &&\
    echo 'done' >> ~/build &&\
    echo 'shift $((OPTIND-1))' >> ~/build &&\
    echo "cd $REPO_DIR" >> ~/build &&\
    echo 'spec=$1' >> ~/build &&\
    echo '[[ $builddep -eq 1 ]] && sudo /usr/bin/yum-builddep $spec' >> ~/build &&\
    echo 'spectool -R -g $spec' >> ~/build &&\
    echo 'rpmbuild -ba $spec' >> ~/build &&\
    echo "DistroDir=$REPO_DIR/epel-${CENTOS_VERSION}" >> ~/build &&\
    echo 'Nvr=$(rpm -q --qf '%{nvr}' --specfile $spec)' >> ~/build &&\
    echo 'Arch=$(rpm -q --qf '%{arch}' --specfile $spec)' >> ~/build &&\
    echo 'if [[ $Arch = "noarch" ]] ;then' >> ~/build &&\
    echo '    mv -f $DistroDir/noarch/* $DistroDir/x86_64' >> ~/build &&\
    echo '    rm -fr $DistroDir/noarch' >> ~/build &&\
    echo '    mkdir -p $DistroDir/i386' >> ~/build &&\
    echo '    cd $DistroDir/i386' >> ~/build &&\
    echo '    rm -f *.noarch.rpm' >> ~/build &&\
    echo '    ln -s ../x86_64/*.noarch.rpm .' >> ~/build &&\
    echo '    cd -' >> ~/build &&\
    echo 'fi' >> ~/build &&\
    echo 'cd $DistroDir' >> ~/build &&\
    echo 'for archDir in SRPMS x86_64 i386 ;do ' >> ~/build &&\
    echo '    createrepo --update --database --verbose --delta $archDir' >> ~/build &&\
    echo 'done ' >> ~/build &&\
    chmod 755 ~/build &&\
    mkdir /tmp/rpmbuild

