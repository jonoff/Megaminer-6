all: libclient.so

submit: libclient.so
	$(shell cd ..;sh submit.sh python)


libclient.so: ../c/*.cpp ../c/*.h
	$(MAKE) -C ../c/ libclient.so
	cp ../c/libclient.so libclient.so


clean:
	rm -f libclient.so
	rm -f *.pyc
