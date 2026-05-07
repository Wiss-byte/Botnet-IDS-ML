import numpy as np
## Prep AfterImage cython package
import os
import subprocess
# import pyximport
# pyximport.install()
import AfterImage as af

class netStat:
    def __init__(self, Lambdas = np.nan, HostLimit=255,HostSimplexLimit=1000):
        if np.isnan(Lambdas):
            self.Lambdas = [5,3,1,.1,.01]
        else:
            self.Lambdas = Lambdas

        self.HostLimit = HostLimit
        self.SessionLimit = HostSimplexLimit*self.HostLimit*self.HostLimit
        self.MAC_HostLimit = self.HostLimit*10

        self.HT_jit = af.incStatDB(limit=self.HostLimit*self.HostLimit)
        self.HT_MI = af.incStatDB(limit=self.MAC_HostLimit)
        self.HT_H = af.incStatDB(limit=self.HostLimit)
        self.HT_Hp = af.incStatDB(limit=self.SessionLimit)

    def findDirection(self,IPtype,srcIP,dstIP,eth_src,eth_dst):
        if IPtype==0:
            lstP = srcIP.rfind('.')
            src_subnet = srcIP[0:lstP:]
            lstP = dstIP.rfind('.')
            dst_subnet = dstIP[0:lstP:]
        elif IPtype==1:
            src_subnet = srcIP[0:round(len(srcIP)/2):]
            dst_subnet = dstIP[0:round(len(dstIP)/2):]
        else:
            src_subnet = eth_src
            dst_subnet = eth_dst
        return src_subnet, dst_subnet

    def updateGetStats(self, IPtype, srcMAC,dstMAC, srcIP, srcProtocol, dstIP, dstProtocol, datagramSize, timestamp):
        # Host BW: Stats on the srcIP's general Sender Statistics
        Hstat = np.zeros((3*len(self.Lambdas,)))
        for i in range(len(self.Lambdas)):
            Hstat[(i*3):((i+1)*3)] = self.HT_H.update_get_1D_Stats(srcIP, timestamp, datagramSize, self.Lambdas[i])

        # MAC.IP: Stats on src MAC-IP relationships
        MIstat = np.zeros((3*len(self.Lambdas,)))
        for i in range(len(self.Lambdas)):
            MIstat[(i*3):((i+1)*3)] = self.HT_MI.update_get_1D_Stats(srcMAC+srcIP, timestamp, datagramSize, self.Lambdas[i])

        # Host-Host BW
        HHstat = np.zeros((7*len(self.Lambdas,)))
        for i in range(len(self.Lambdas)):
            HHstat[(i*7):((i+1)*7)] = self.HT_H.update_get_1D2D_Stats(srcIP, dstIP,timestamp,datagramSize,self.Lambdas[i])

        # Host-Host Jitter
        HHstat_jit = np.zeros((3*len(self.Lambdas,)))
        for i in range(len(self.Lambdas)):
            HHstat_jit[(i*3):((i+1)*3)] = self.HT_jit.update_get_1D_Stats(srcIP+dstIP, timestamp, 0, self.Lambdas[i],isTypeDiff=True)

        # Host-Port to Host-Port BW
        HpHpstat = np.zeros((7*len(self.Lambdas,)))
        if srcProtocol == 'arp':
            for i in range(len(self.Lambdas)):
                HpHpstat[(i*7):((i+1)*7)] = self.HT_Hp.update_get_1D2D_Stats(srcMAC, dstMAC, timestamp, datagramSize, self.Lambdas[i])
        else:
            for i in range(len(self.Lambdas)):
                HpHpstat[(i*7):((i+1)*7)] = self.HT_Hp.update_get_1D2D_Stats(srcIP+srcProtocol, dstIP+dstProtocol, timestamp, datagramSize, self.Lambdas[i])

        return np.concatenate((MIstat, Hstat, HHstat, HHstat_jit, HpHpstat))

    def getNetStatHeaders(self):
        MIstat_headers = []
        Hstat_headers = []
        HHstat_headers = []
        HHjitstat_headers = []
        HpHpstat_headers = []

        for i in range(len(self.Lambdas)):
            MIstat_headers += ["MI_dir_"+h for h in self.HT_MI.getHeaders_1D(Lambda=self.Lambdas[i],ID=None)]
            Hstat_headers  += ["H_"+h for h in self.HT_H.getHeaders_1D(Lambda=self.Lambdas[i],ID=None)]
            HHstat_headers += ["HH_"+h for h in self.HT_H.getHeaders_1D2D(Lambda=self.Lambdas[i],IDs=None,ver=2)]
            HHjitstat_headers += ["HH_jit_"+h for h in self.HT_jit.getHeaders_1D(Lambda=self.Lambdas[i],ID=None)]
            HpHpstat_headers  += ["HpHp_"+h for h in self.HT_Hp.getHeaders_1D2D(Lambda=self.Lambdas[i],IDs=None,ver=2)]

        return MIstat_headers + Hstat_headers + HHstat_headers + HHjitstat_headers + HpHpstat_headers