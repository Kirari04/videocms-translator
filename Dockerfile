FROM debian

WORKDIR /app

RUN apt update && apt upgrade -y
# RUN apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev -y
RUN apt install python3 python3-pip -y
RUN apt install git git-lfs -y
RUN git-lfs install
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip3 install transformers
RUN pip3 install flask

COPY run.py .
COPY nllb-200-distilled-600M/ ./nllb-200-distilled-600M

EXPOSE 5000

CMD ["/usr/bin/python3", "./run.py"]