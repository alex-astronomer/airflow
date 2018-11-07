# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand

import imp
import logging
import os
import sys
import subprocess

logger = logging.getLogger(__name__)

# Kept manually in sync with airflow.__version__
version = imp.load_source(
    'airflow.version', os.path.join('airflow', 'version.py')).version

PY3 = sys.version_info[0] == 3


# See LEGAL-362
def verify_gpl_dependency():
    # The Read the Docs build environment [1] does a pip install of Airflow which cannot
    # be overridden with custom environment variables, so we detect the READTHEDOCS env
    # var they provide to set the env var that avoids the GPL dependency on install when
    # building the docs site.
    # [1]: http://docs.readthedocs.io/en/latest/builds.html#build-environment
    if os.getenv("READTHEDOCS") == "True":
        os.environ["SLUGIFY_USES_TEXT_UNIDECODE"] = "yes"

    if not os.getenv("AIRFLOW_GPL_UNIDECODE") and not os.getenv("SLUGIFY_USES_TEXT_UNIDECODE") == "yes":
        raise RuntimeError("By default one of Airflow's dependencies installs a GPL "
                           "dependency (unidecode). To avoid this dependency set "
                           "SLUGIFY_USES_TEXT_UNIDECODE=yes in your environment when you "
                           "install or upgrade Airflow. To force installing the GPL "
                           "version set AIRFLOW_GPL_UNIDECODE")


class Tox(TestCommand):
    user_options = [('tox-args=', None, "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = ''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(args=self.tox_args.split())
        sys.exit(errno)


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


class CompileAssets(Command):
    """
    Custom compile assets command to compile and build the frontend
    assets using npm and webpack.
    """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.call('./airflow/www_rbac/compile_assets.sh')


def git_version(version):
    """
    Return a version to identify the state of the underlying git repo. The version will
    indicate whether the head of the current git-backed working directory is tied to a
    release tag or not : it will indicate the former with a 'release:{version}' prefix
    and the latter with a 'dev0' prefix. Following the prefix will be a sha of the current
    branch head. Finally, a "dirty" suffix is appended to indicate that uncommitted
    changes are present.
    """
    repo = None
    try:
        import git
        repo = git.Repo('.git')
    except ImportError:
        logger.warning('gitpython not found: Cannot compute the git version.')
        return ''
    except Exception as e:
        logger.warning('Cannot compute the git version. {}'.format(e))
        return ''
    if repo:
        sha = repo.head.commit.hexsha
        if repo.is_dirty():
            return '.dev0+{sha}.dirty'.format(sha=sha)
        # commit is clean
        return '.release:{version}+{sha}'.format(version=version, sha=sha)
    else:
        return 'no_git_version'


def write_version(filename=os.path.join(*['airflow',
                                          'git_version'])):
    text = "{}".format(git_version(version))
    with open(filename, 'w') as a:
        a.write(text)


async_packages = [
    'greenlet>=0.4.9',
    'eventlet>= 0.9.7',
    'gevent>=0.13'
]
atlas = ['atlasclient>=0.1.2']
azure_blob_storage = ['azure-storage>=0.34.0']
azure_data_lake = [
    'azure-mgmt-resource==1.2.2',
    'azure-mgmt-datalake-store==0.4.0',
    'azure-datalake-store==0.0.19'
]
cassandra = ['cassandra-driver>=3.13.0']
celery = [
    'celery>=4.1.1, <4.2.0',
    'flower>=0.7.3, <1.0'
]
cgroups = [
    'cgroupspy>=0.1.4',
]
# major update coming soon, clamp to 0.x
cloudant = ['cloudant>=0.5.9,<2.0']
crypto = ['cryptography>=0.9.3']
dask = [
    'distributed>=1.17.1, <2'
]
databricks = ['requests>=2.5.1, <3']
datadog = ['datadog>=0.14.0']
doc = [
    'mock',
    'sphinx>=1.2.3',
    'sphinx-argparse>=0.1.13',
    'sphinx-rtd-theme>=0.1.6',
    'Sphinx-PyPI-upload>=0.2.1'
]
docker = ['docker>=3.0.0']
druid = ['pydruid>=0.4.1']
elasticsearch = [
    'elasticsearch>=5.0.0,<6.0.0',
    'elasticsearch-dsl>=5.0.0,<6.0.0'
]
emr = ['boto3>=1.0.0, <1.8.0']
gcp_api = [
    'httplib2>=0.9.2',
    'google-api-python-client>=1.6.0, <2.0.0dev',
    'google-auth>=1.0.0, <2.0.0dev',
    'google-auth-httplib2>=0.0.1',
    'google-cloud-container>=0.1.1',
    'PyOpenSSL',
    'pandas-gbq'
]
github_enterprise = ['Flask-OAuthlib>=0.9.1']
google_auth = ['Flask-OAuthlib>=0.9.1']
hdfs = ['snakebite>=2.7.8']
hive = [
    'hmsclient>=0.1.0',
    'pyhive>=0.6.0',
]
jdbc = ['jaydebeapi>=1.1.1']
jenkins = ['python-jenkins>=0.4.15']
jira = ['JIRA>1.0.7']
kerberos = ['pykerberos>=1.1.13',
            'requests_kerberos>=0.10.0',
            'thrift_sasl>=0.2.0',
            'snakebite[kerberos]>=2.7.8']
kubernetes = ['kubernetes>=3.0.0',
              'cryptography>=2.0.0']
ldap = ['ldap3>=0.9.9.1']
mssql = ['pymssql>=2.1.1']
mysql = ['mysqlclient>=1.3.6']
oracle = ['cx_Oracle>=5.1.2']
password = [
    'bcrypt>=2.0.0',
    'flask-bcrypt>=0.7.1',
]
pinot = ['pinotdb>=0.1.1']
postgres = ['psycopg2-binary>=2.7.4']
qds = ['qds-sdk>=1.9.6']
rabbitmq = ['librabbitmq>=1.6.1']
redis = ['redis>=2.10.5']
s3 = ['boto3>=1.7.0, <1.8.0']
salesforce = ['simple-salesforce>=0.72']
samba = ['pysmbclient>=0.1.3']
segment = ['analytics-python>=1.2.9']
sendgrid = ['sendgrid>=5.2.0']
slack = ['slackclient>=1.0.0']
mongo = ['pymongo>=3.6.0']
snowflake = ['snowflake-connector-python>=1.5.2',
             'snowflake-sqlalchemy>=1.1.0']
ssh = ['paramiko>=2.1.1', 'pysftp>=0.2.9', 'sshtunnel>=0.1.4,<0.2']
statsd = ['statsd>=3.0.1, <4.0']
vertica = ['vertica-python>=0.5.1']
webhdfs = ['hdfs[dataframe,avro,kerberos]>=2.0.4']
winrm = ['pywinrm==0.2.2']
zendesk = ['zdesk']

all_dbs = postgres + mysql + hive + mssql + hdfs + vertica + cloudant + druid + pinot \
    + cassandra + mongo

devel = [
    'click==6.7',
    'freezegun',
    'jira',
    'lxml>=4.0.0',
    'mock',
    'mongomock',
    'moto==1.1.19',
    'nose',
    'nose-ignore-docstring==0.2',
    'nose-timer',
    'parameterized',
    'paramiko',
    'pysftp',
    'pywinrm',
    'qds-sdk>=1.9.6',
    'rednose',
    'requests_mock',
    'flake8==3.5.0'
]

if not PY3:
    devel += ['unittest2']

devel_minreq = devel + kubernetes + mysql + doc + password + s3 + cgroups
devel_hadoop = devel_minreq + hive + hdfs + webhdfs + kerberos
devel_all = (sendgrid + devel + all_dbs + doc + samba + s3 + slack + crypto + oracle +
             docker + ssh + kubernetes + celery + azure_blob_storage + redis + gcp_api +
             datadog + zendesk + jdbc + ldap + kerberos + password + webhdfs + jenkins +
             druid + pinot + segment + snowflake + elasticsearch + azure_data_lake +
             atlas)

# Snakebite & Google Cloud Dataflow are not Python 3 compatible :'(
if PY3:
    devel_ci = [package for package in devel_all if package not in
                ['snakebite>=2.7.8', 'snakebite[kerberos]>=2.7.8']]
else:
    devel_ci = devel_all


def do_setup():
    verify_gpl_dependency()
    write_version()
    setup(
        name='apache-airflow',
        description='Programmatically author, schedule and monitor data pipelines',
        license='Apache License 2.0',
        version=version,
        packages=find_packages(exclude=['tests*']),
        package_data={'': ['airflow/alembic.ini', "airflow/git_version"]},
        include_package_data=True,
        zip_safe=False,
        scripts=['airflow/bin/airflow'],
        install_requires=[
            'alembic>=0.9, <1.0',
            'bleach~=2.1.3',
            'configparser>=3.5.0, <3.6.0',
            'croniter>=0.3.17, <0.4',
            'dill>=0.2.2, <0.3',
            'flask>=0.12.4, <0.13',
            'flask-appbuilder==1.12.1',
            'flask-admin==1.4.1',
            'flask-caching>=1.3.3, <1.4.0',
            'flask-login>=0.3, <0.5',
            'flask-swagger==0.2.13',
            'flask-wtf>=0.14.2, <0.15',
            'funcsigs==1.0.0',
            'future>=0.16.0, <0.17',
            'gitpython>=2.0.2',
            'gunicorn>=19.4.0, <20.0',
            'iso8601>=0.1.12',
            'jinja2>=2.7.3, <2.9.0',
            'lxml>=4.0.0',
            'markdown>=2.5.2, <3.0',
            'pandas>=0.17.1, <1.0.0',
            'pendulum==1.4.4',
            'psutil>=4.2.0, <6.0.0',
            'pygments>=2.0.1, <3.0',
            'python-daemon>=2.1.1, <2.2',
            'python-dateutil>=2.3, <3',
            'python-nvd3==0.15.0',
            'requests>=2.5.1, <3',
            'setproctitle>=1.1.8, <2',
            'sqlalchemy>=1.1.15, <1.2.0',
            'tabulate>=0.7.5, <=0.8.2',
            'tenacity==4.8.0',
            'thrift>=0.9.2',
            'tzlocal>=1.4',
            'unicodecsv>=0.14.1',
            'werkzeug>=0.14.1, <0.15.0',
            'zope.deprecation>=4.0, <5.0',
        ],
        setup_requires=[
            'docutils>=0.14, <1.0',
        ],
        extras_require={
            'all': devel_all,
            'devel_ci': devel_ci,
            'all_dbs': all_dbs,
            'atlas': atlas,
            'async': async_packages,
            'azure_blob_storage': azure_blob_storage,
            'azure_data_lake': azure_data_lake,
            'cassandra': cassandra,
            'celery': celery,
            'cgroups': cgroups,
            'cloudant': cloudant,
            'crypto': crypto,
            'dask': dask,
            'databricks': databricks,
            'datadog': datadog,
            'devel': devel_minreq,
            'devel_hadoop': devel_hadoop,
            'doc': doc,
            'docker': docker,
            'druid': druid,
            'elasticsearch': elasticsearch,
            'emr': emr,
            'gcp_api': gcp_api,
            'github_enterprise': github_enterprise,
            'google_auth': google_auth,
            'hdfs': hdfs,
            'hive': hive,
            'jdbc': jdbc,
            'jira': jira,
            'kerberos': kerberos,
            'kubernetes': kubernetes,
            'ldap': ldap,
            'mongo': mongo,
            'mssql': mssql,
            'mysql': mysql,
            'oracle': oracle,
            'password': password,
            'pinot': pinot,
            'postgres': postgres,
            'qds': qds,
            'rabbitmq': rabbitmq,
            'redis': redis,
            's3': s3,
            'salesforce': salesforce,
            'samba': samba,
            'sendgrid': sendgrid,
            'segment': segment,
            'slack': slack,
            'snowflake': snowflake,
            'ssh': ssh,
            'statsd': statsd,
            'vertica': vertica,
            'webhdfs': webhdfs,
            'winrm': winrm
        },
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: System :: Monitoring',
        ],
        author='Apache Software Foundation',
        author_email='dev@airflow.incubator.apache.org',
        url='http://airflow.incubator.apache.org/',
        download_url=(
            'https://dist.apache.org/repos/dist/release/incubator/airflow/' + version),
        cmdclass={
            'test': Tox,
            'extra_clean': CleanCommand,
            'compile_assets': CompileAssets
        },
        python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    )


if __name__ == "__main__":
    do_setup()
