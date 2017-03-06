FROM fedora

# there is an issue in either fedora-review or mock where you need to run dnf makecache first
RUN dnf install -y fedora-review fedora-review-plugin-java sudo && dnf clean all && dnf makecache

# the ordinary non-root user for running fedora-review
ENV USER=reviewer
# create a new non root user and add to group: wheel, mock
RUN useradd -m -g mock -G wheel -d /home/$USER $USER && echo 'reviewer' | passwd --stdin $USER  \
    && sed -i -e "s|# %wheel|$USER|" /etc/sudoers

# copy some utility scripts
COPY scripts/ /home/$USER/scripts/

RUN chmod -R 755 /home/$USER/scripts/

USER $USER

ENTRYPOINT ["newgrp"]

