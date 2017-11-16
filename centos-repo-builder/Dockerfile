FROM centos:@CENTOS_VERSION@
ARG CENTOS_VERSION=@CENTOS_VERSION@
ARG USER=builder
ARG UID=1000
ARG REPO_DIR="/repo"
ARG RPMBUILD_TOPDIR="/rpmbuild"
ARG RPMBUILD_SOURCE_DIR="/rpmbuild"

## Override this if you want to test zanata-docker-files pull requests
ARG BRANCH=master

LABEL build="20171116" \
    description="Build RPMs and create repository for Fedora People repository"

ENV EXTRA_PACKAGES="java-1.8.0-openjdk-devel"

ENTRYPOINT ["/home/builder/build"]

RUN yum install -y createrepo rpm-build rpmdevtools sudo yum-utils $EXTRA_PACKAGES && yum clean all

# create the user and home
RUN useradd -m -G wheel -d /home/builder -u $UID $USER && mkdir -p $REPO_DIR && chown -R $USER $REPO_DIR &&\
    echo "$USER    ALL=(ALL)    NOPASSWD: /usr/bin/yum-builddep" >> /etc/sudoers.d/$USER &&\
    echo "Defaults lecture = never" >> /etc/sudoers.d/lecture

VOLUME $REPO_DIR $RPMBUILD_SOURCE_DIR

USER $USER
WORKDIR /home/builder
ADD "https://raw.githubusercontent.com/zanata/zanata-docker-files/$BRANCH/centos-repo-builder/_rpmmacros" .rpmmacros
ADD "https://raw.githubusercontent.com/zanata/zanata-docker-files/$BRANCH/centos-repo-builder/build" build
RUN for v in CENTOS_VERSION REPODIR RPMBUILD_TOPDIR RPMBUILD_SOURCEDIR ; do\
        sed -i -e "s/@$v@/$$v/g" .rpmmacros &&\
        sed -i -e "s/@$v@/$$v/g" build ;\
    done &&\
    mkdir -p $RPMBUILD_TOPDIR

