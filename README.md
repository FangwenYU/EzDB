What is EzDB?
=================
EzDB is a toolkit to generate DB package based on db XML file (to be defined).


How to run EzDB?
================
EzDB comes with a python package called ``ezdb`` and a standalone python script ``ezdb.py`` which uses the package ``ezdb``.

You can either choose to install the package ``ezdb`` to your python package repository or just use it together with ``ezdb.py``.


To install package ``ezdb``, you can run the following command:


    python setup.py install



Configure the options
---------------------
Before running the script ``ezdb.py``, you need to configure two configuration files:

1. **logging.cnf** (configure the logging options for the toolkit).
2. **ezdb.cnf** (configure where to get the raw XML files and where to put the generated DB package)

###logging.cnf


For the logging.cnf, by default the log will be written to both command line and a log file. You can modify the configuration file
to suit your requirements.

You may want to change the log file file path. To do this, go the section ``handler_filehandler``. By default it looks like as
below.


      [handler_fileHandler]
      class=FileHandler
      level=DEBUG
      formatter=simpleFormatter
      args=('ezdb.log', 'w',)


Pay attention to the key **args**. Currently, there are two items, the first one 'ezdb.log' is the log file name, you can
modify it to point to your desired log file path; the second 'w' is used to specify the log file open mode. 'w' means the log
file will be purged for each run, if you use 'a', the log file will be opened using ``append`` mode.

###ezdb.cnf

There are two sections in this configuration file:

1. **snapshot_function**

   This parameter is used to indicate whether the db package generated is used for snapshot database. If the value is set to
   **true**, a column called **SNAPSHOT_ID** will be added to the table, and the primary key (if exists) will also be updated
   to include the column **SNAPSHOT_ID**.

   For example, suppose there is one table ``LO_DEMO``


	   create table lo_demo
	   (
	      demo_id number,
	      demo_desc varchar2(50)
	   );

   	  alter table lo_demo add constraint pk_lo_demo primary key(demo_id);

If the ``snapshot_function`` is enabled. The table in the snapshot db will we like this -


	   create table lo_demo
	   (
	     snapshot_id number,
	     demo_id number,
	     demo_desc varchar2(50)
	   );
	
	   alter table lo_demo add constraint pk_lo_demo primary key(snapshot_id, demo_id);



2. **db_comipler**

   * common_db_dir

   This tells where the common/utility scripts (i.e. the DB_SCRIPTS provided in this toolkit). These scripts will be copied
   into the final DB package.

   * source_db_dir

     This tells where the source XML files are put. The folder structure should be like this -
	
	    DB
	    |- TABLE
	    |- VIEW
	    |- PROCEDURE
	    |- PACKAGE
	    |- FUNCTION
	    |- TYPE
	    |- TRIGGER

For example, all the table XML files should be put in the folder ``TABLE``


   * target_db_dir

   This tells where the DB package (DB.tgz) will be generated.

   * release_number
   This tells the release number of the database. There will be a file called 'RELEASE.TXT' generated in the final DB package,
   and the release number specified here will be put in that file.


Run ``ezdb.py``
-------------------
With the configuration files setup correctly, it's no sweat to run the script ``ezdb.py`` to generate the db package. Just run the
following command:

``python ezdb.py``

You can check the log from the log file you specified in the configuration file ``logging.cnf``


How to install DB?
==================
After running ``ezdb.py``, you will get a ``DB.tgz`` in the directory you specified. You can deliver it to the clients for database
installation.

To install the db, go to the folder ``DB\TOOLS\SCHEMA_CREATION`` and run the batch file ``IFS.bat`` directly. You will be asked to
specify some parameters, like schema name, password, tablespaces, etc. Just follow the instruction to get the db set up.

How to upgrade DB?
==================
To upgrade a existing DB, go to the folder ``DB\TOOLS\AUTO_UPGRADE`` and the run the batch file ``UPGRADE_BATCH.BAT``. You can either
double-click it directly and input the relevant the parameters when you are promoted to do so, or launch the command line and run this
bat file with the parameters.

Open the command line and start the batch file with the parameter ``?`` to see the help message.


    Usage: UPGRADE_BATCH.BAT [central connection] [output dir] [DB dir] [exit on error] [upgrade password]
      {central connection} : Connection string to the schema to upgrade. Expected format: login/password@db
              {Output dir} : Optional. Output directory for generated upgrade scripts and log files
                             If not filled, current script directory
                  {DB dir} : Optional. DB directory to use for upgrade
                             If not filled, derived from current script directory: ..\..
           {exit on error} : Optional. Specify if you want the script to stop on error. Default : N
        {upgrade password} : Optional. Central user password used during the upgrade.
                             if not filled, "UPGRADING" is used.
    Examples:
    UPGRADE_BATCH test/a@orcl
    UPGRADE_BATCH test@orcl c:\tmp
    UPGRADE_BATCH test/a@orcl c:\tmp c:\db
    UPGRADE_BATCH test/a@orcl c:\tmp c:\db Y
    UPGRADE_BATCH test/a@orcl c:\tmp c:\db N upgrading



