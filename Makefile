## warp
NAME = warp
VERSION = 0.1
TARFILE = $(NAME)-$(VERSION).tar.gz
PYSOURCES = client_transfer_controller.py  progress.py \
		client_udt_manager.py	       server.py \
		common_tools.py		       server_transfer_controller.py \
		config.py		       server_udt_manager.py \
		connection.py		       transfer_manager.py \
		file_transfer_agent.py	       warp.py \
		forward.py
SCRIPTS = warp.sh server.sh
 
## Generic
RPMDIRS = SOURCES BUILD SRPMS RPMS BUILDROOT

## Help
HELPTEXT = "\
	make help       -- This message \n\
	make rpm        -- makes warp rpm  \n\
	make clean      -- cleans everything \n\
	"

help:
	@ echo -e $(HELPTEXT)

$(RPMDIRS):
	mkdir $@

SOURCES/$(TARFILE): $(RPMDIRS) 
	- /bin/rm -rf $(NAME)-$(VERSION)
	mkdir $(NAME)-$(VERSION) 
	cp $(PYSOURCES) $(SCRIPTS) $(NAME)-$(VERSION)
	tar czf $@ $(NAME)-$(VERSION)

rpm: SOURCES/$(TARFILE)
	rpmbuild -ba --buildroot=$(PWD)/BUILDROOT $(NAME).spec

	
clean:
	/bin/rm -rf $(NAME)-$(VERSION) $(RPMDIRS)
