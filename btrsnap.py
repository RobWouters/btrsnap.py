#!/usr/bin/python3

import os
import subprocess as sp

from datetime import datetime

class Snapshot:
    def __init__(self, interval, source, destination=None, readonly=True, keep=0):
        self.keep = keep
        self.interval = interval
        self.source = source
        if destination is None:
            name = os.path.dirname(source + '/')
            self._destination = os.path.join(source, '..', '{}-snapshots'.format(name))
        else:
            self._destination = destination
        self.readonly = readonly

    @property
    def timestamp(self):
        now = datetime.now()
        now = now.replace(minute=0)
        return now.strftime('%Y-%m-%d-%H.%M')

    @property
    def filename(self):
        return '{}-{}'.format(self.timestamp, self.interval)

    @property
    def destination(self):
        return os.path.join(self._destination, self.filename)

    def create(self):
        cmd = [
            '/sbin/btrfs',
            'subvolume',
            'snapshot'
        ]
        if self.readonly:
            cmd.append('-r')
        cmd.append(self.source)
        cmd.append(self.destination)
        sp.call(cmd)
        self.delete_extra()

    @property
    def snapshots(self):
        ret = []
        for entry in os.listdir(self._destination):
            if entry.endswith(self.interval):
                ret.append(entry)
        ret.sort()
        return ret

    def delete_extra(self):
        if self.keep is None:
            return
        keep = int(self.keep)
        for snapshot in self.snapshots[:-keep]:
            self.delete(snapshot)

    def delete(self, snapshot):
        cmd = [
            '/sbin/btrfs',
            'subvolume',
            'delete',
            os.path.join(self._destination, snapshot),
        ]
        sp.call(cmd)


def main(interval, source, keep: ('Maximum number of snapshots to store', 'option', 'k'), destination=None, readonly=True):
    snapshot = Snapshot(interval, source, destination, readonly, keep)
    snapshot.create()

if __name__ == '__main__':
    import plac
    plac.call(main)
