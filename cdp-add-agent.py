#!/usr/bin/env python

import logging
import r1soft

logger = logging.getLogger('cdp-add-agent')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
logger.propagate = False

if __name__ == '__main__':
    import sys
    import os

    parser = r1soft.create_basic_option_parser()
    parser.add_option('-d', '--description', dest='description',
        default=None,
        help='Custom description field, default is the same as hostname, applied to all hosts')
    parser.add_option('-D', '--use-db-addon', dest='use_db_addon',
        action='store_true', default=False,
        help='Use the CDP DB addon')
    parser.add_option('--db-user', dest='sqluser',
        help='MySQL user for DB addon')
    parser.add_option('--db-pass', dest='sqlpass',
        help='MySQL pass for DB addon')
    parser.add_option('-R', '--recovery-point-limit', dest='recovery_point_limit',
        type=int, default=30,
        help='Number of recovery points to keep')
    options, args = parser.parse_args()

    cdp_host = options.hostname
    username = options.username
    password = options.password
    use_db_addon = options.use_db_addon
    recovery_point_limit = options.recovery_point_limit
    sqluser = options.sqluser
    sqlpass = options.sqlpass
    for hostname in args:
        if options.description is None:
            description = hostname
        else:
            description = '%s (%s)' % (options.description, hostname)
        logger.info('Setting up backups for host (%s) on CDP server (%s) with description: %s',
            hostname, cdp_host, description)
        client = r1soft.cdp3.MetaClient(r1soft.cdp3.format_wsdl_url(cdp_host, '%s'),
            username=username, password=password)
        logger.debug('Creating special types...')
        CompressionType = client.DiskSafe.factory.create('diskSafe.compressionType')
        CompressionLevel = client.DiskSafe.factory.create('diskSafe.compressionLevel')
        DeviceBackupType = client.DiskSafe.factory.create('diskSafe.deviceBackupType')
        FrequencyType = client.Policy2.factory.create('frequencyType')
        FrequencyValues = client.Policy2.factory.create('frequencyValues')
        logger.debug('Created special types')
        logger.debug('Getting volumes...')
        volumes = client.Volume.service.getVolumes()
        volume = volumes[0]
        logger.info('Found %d volumes, using volume %s', len(volumes), volume.name)
        logger.debug('Creating agent for host: %s', hostname)
        agent = client.Agent.service.createAgent(
            hostname=hostname,
            portNumber=1167,
            description=description,
            databaseAddOnEnabled=use_db_addon
        )
        logger.info('Created agent for host (%s) with ID: %s', hostname, agent.id)
        logger.debug('Creating disksafe for agent (%s) on volume (%s)', agent.id, volume.id)
        disksafe = client.DiskSafe.service.createDiskSafeOnVolume(
            name=hostname,
            agentID=agent.id,
            volumeID=volume.id,
            compressionType=CompressionType.QUICKLZ,
            compressionLevel=CompressionLevel.LOW,
            deviceBackupType=DeviceBackupType.AUTO_ADD_DEVICES,
            protectStorageConfiguration=True,
            protectUnmountedDevices=False
        )
        logger.info('Created disksafe with ID: %s', disksafe.id)
        FrequencyValues.hoursOfDay = [0]
        FrequencyValues.startingMinute = 0
        logger.debug('Creating policy for agent (%s) on disksafe (%s)',
            hostname, disksafe.id)
        policy = client.Policy2.factory.create('policy')
        policy.enabled = True
        policy.name = hostname
        policy.description = description
        policy.diskSafeID = disksafe.id
        policy.mergeSchedulFrequencyType = FrequencyType.ON_DEMAND
        policy.replicationScheduleFrequencyType = FrequencyType.DAILY
        policy.replicationScheduleFrequencyValues = FrequencyValues
        policy.recoveryPointLimit = recovery_point_limit
        policy.forceFullBlockScan = False
        if use_db_addon:
            dbi = client.Policy2.factory.create('databaseInstance')
            dbi.dataBaseType = client.Policy2.factory.create('dataBaseType').MYSQL
            dbi.enabled = True
            dbi.hostName = '127.0.0.1'
            dbi.name = 'default'
            dbi.username = sqluser
            dbi.password = sqlpass
            dbi.portNumber = 3306
            dbi.useAlternateDataDirectory = False
            dbi.useAlternateHostname = True
            dbi.useAlternateInstallDirectory = False
            policy.databaseInstanceList = [dbi]

        policy = client.Policy2.service.createPolicy(policy=policy)
        logger.info('Created policy with ID: %s', policy.id)
        logger.info('Finished setting up backups for host: %s', hostname)
