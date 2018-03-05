FROM ubuntu
WORKDIR /codec_compare

# DEPENDENCIES
RUN apt-get clean && apt-get update && apt-get install -y \
    wget \
    unzip \
    g++ \
    make \
    patchelf \
    bzip2 \
    pkg-config \
    yasm \
    subversion \
    python \
    imagemagick \
    python-pip && \
    pip install plotly

# JPEG
RUN mkdir -p /tools && \
    cd /tools && \
    wget -O jpeg.zip https://jpeg.org/downloads/jpegxt/reference1367abcd89.zip && \
    unzip jpeg.zip -d jpeg && \
    rm -f jpeg.zip && \
    cd jpeg && \
    ./configure && \
    make

# KAKADU
RUN mkdir -p /tools && \
    cd /tools && \
    wget -O kakadu.zip http://kakadusoftware.com/wp-content/uploads/2014/06/KDU7A2_Demo_Apps_for_Ubuntu-x86-64_170827.zip && \
    unzip kakadu.zip -d kakadu && \
    rm -f kakadu.zip && \
    patchelf --set-rpath '$ORIGIN/' /tools/kakadu/KDU7A2_Demo_Apps_for_Ubuntu-x86-64_170827/kdu_compress && \
    patchelf --set-rpath '$ORIGIN/' /tools/kakadu/KDU7A2_Demo_Apps_for_Ubuntu-x86-64_170827/kdu_expand && \
    patchelf --set-rpath '$ORIGIN/' /tools/kakadu/KDU7A2_Demo_Apps_for_Ubuntu-x86-64_170827/kdu_v_compress && \
    patchelf --set-rpath '$ORIGIN/' /tools/kakadu/KDU7A2_Demo_Apps_for_Ubuntu-x86-64_170827/kdu_v_expand

# WEBP
RUN mkdir -p /tools && \
    cd /tools && \
    wget -O libwebp.tar.gz https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-0.6.1-linux-x86-64.tar.gz  && \
    tar xvzf libwebp.tar.gz && \
    rm -f libwebp.tar.gz

# HEVC
RUN mkdir -p /tools && \
    cd /tools && \
    svn checkout https://hevc.hhi.fraunhofer.de/svn/svn_HEVCSoftware/tags/HM-16.9+SCM-8.0/ && \
    cd HM-16.9+SCM-8.0/build/linux && \
    make

# VMAF, FFMPEG
RUN mkdir -p /tools && \
    cd /tools && \
    wget -O vmaf.zip https://github.com/Netflix/vmaf/archive/v1.3.1.zip && \
    unzip vmaf.zip && \
    rm -f vmaf.zip && \
    cd vmaf-1.3.1 && \
    make && \
    make install && \
    cd /tools && \
    wget -O ffmpeg.tar.bz2 http://ffmpeg.org/releases/ffmpeg-3.4.1.tar.bz2 && \
    tar -vxjf ffmpeg.tar.bz2 && \
    rm ffmpeg.tar.bz2 && \
    cd ffmpeg-3.4.1 && \
    ./configure --enable-libvmaf && \
    make install

# TO ADD ANOTHER
# ADD /local/path/to/bin /tools/bin
# ^ This will add the file from the host machine into the container. In this case the bin is accessible at: `/tools/bin`.
