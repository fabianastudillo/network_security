FROM fabianastudillo/labsecuc:latest AS builder

# Copy the source code to the image
COPY .  /oracle
WORKDIR /oracle

RUN make


FROM fabianastudillo/labsecuc:latest

# Copy the executable binaries to the image
COPY --from=builder /oracle/build /oracle
WORKDIR /oracle

CMD ./server
