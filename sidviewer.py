import glob
import itertools
import os
import sys
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.dates as mdates
import matplotlib.font_manager as font_m
import numpy
import scipy.signal as sc
import wx
import xlrd as xl
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.mlab import movavg
from scipy import signal as sc
from scipy import stats

matplotlib.rcParams.update({'font.size': 25}) #36

class SepViewer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.figure = Figure()
        
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.figure.patch.set_facecolor('white')
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

    def draw(self, sid1, rsdate, shade, flare):
        """ Simple """
        # if controller.sid1 and controller.sid2:
        #     tsid1 = controller.sid1[1]
        #     xsid1 = controller.sid1[0]
        #     tsid2 = controller.sid2[1]
        #     xsid2 = controller.sid2[0]

        #     self.axes1 = self.figure.add_subplot(111)
        #     self.axes1.plot(xsid1, tsid1)
        #     self.axes1.plot(xsid2, tsid2)
        #     self.fmataxes(self.axes1)
        tsid1 = sid1[1]
        xsid1 = sid1[0]

        self.axes1 = self.figure.add_subplot(211)
        self.axes1.plot(xsid1, tsid1, color='green', linewidth=2)
        self.anotateAxes(self.axes1,tsid1,rsdate,shade,flare)
        self.fmataxes(self.axes1)

    def draw2(self, controller, sid1, sid2):
        """ Superimposed """
        tsid1 = sid1[1]
        xsid1 = sid1[0]
        tsid2 = sid2[1]
        xsid2 = sid2[0]
        

        # Scatter Plot
        if False:
            self.axes1 = self.figure.add_subplot(111)
            lbl = "y= {0:.3f}x + {1:.3f}".format(controller.slope, controller.intercept)
            self.axes1.scatter(tsid1,tsid2, alpha=0.5, marker='o', color='darkgreen')            
            self.axes1.ticklabel_format(style='sci', axis='both', scilimits=(0, 0))
            self.axes1.plot(numpy.unique(tsid1), numpy.poly1d(numpy.polyfit(tsid1, tsid2, 1))(numpy.unique(tsid1)), linewidth=3, label=lbl)
            self.axes1.legend(loc=2)
            self.axes1.set_xlabel('MIT-PH Relative Strength')
            self.axes1.set_ylabel('MIT-PH2 Relative Strenth')

            dlg = wx.TextEntryDialog(self, 'Plot Title', 'Viewer')
            dlg.SetValue('Scatter Plot: MIT-PH & MIT-PH-2 @ NWC')
            if dlg.ShowModal() == wx.ID_OK:
                self.axes1.set_title(dlg.GetValue())
            #self.axes1.set_xlim(0,10e5)
            #self.axes1.set_ylim(0,10e5)

        if True:
            self.axes1 = self.figure.add_subplot(211)
            ld1 = self.axes1.plot(xsid1, tsid1, color='blue', linewidth=2, label='MIT-PH')
            self.fmataxes(self.axes1)
            self.axes2 = self.axes1.twinx()
            ld2 = self.axes2.plot(xsid2, tsid2, color='green', linewidth=2, label='MIT-PH2')

            lds = ld1 + ld2
            labs = [ l.get_label() for l in lds]
            self.axes1.legend(lds,labs, loc=2)
            #self.axes1.legend(loc=3)
            self.fmataxes(self.axes2)

    def draw3(self, sid1, rfal, xrfal):
        """ Rainfall  """
        tsid1 = sid1[1]
        xsid1 = sid1[0]
                
        self.axes1 = self.figure.add_subplot(211)
        self.axes2 = self.figure.add_subplot(212)     

        self.axes1.plot(xsid1, tsid1, color='darkgreen', linewidth=2)
        self.fmataxes(self.axes1)

        self.axes2.set_ylabel("10 min Rainfall")
        self.axes2.set_xlabel("UTC Time")
        self.axes2.bar(xrfal, rfal, color='skyblue', width=0.005)

        self.axes2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.axes2.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
        #self.axes2.set_xlabel("UTC Time")

    def draw4(self, sid1, rsdate, shade, flare):
        """ Derivative Plot """
        tsid1 = sid1[1]
        xsid1 = sid1[0]

        self.axes1 = self.figure.add_subplot(211)
        self.axes1.plot(xsid1, tsid1, color='steelblue')
        #self.anotateAxes(self.axes1, tsid1, rsdate, shade, flare)
        #self.axes1.set_ylim(-1e3,1e3)
        self.fmataxes(self.axes1) 

    def settwilight(self,rsdate):
        tstamps = ['03:52', '04:40','15:31', '17:14', '18:11', '19:41']
        strstamps = ['1', '2','C2.0', 'C1.2', '3', '4']
        
        dtstamps = []
        dat = []

        for x in tstamps:            
            #dtstamps.append(datetime.strptime(temp_d+x, t_format))            
            j = x.split(':')
            dtstamps.append(rsdate + timedelta(hours=int(j[0]),minutes=int(j[1])))
            index = (int(j[0])*60*60) + int(j[1])*60
            index = (index/5) - 1
            dat.append(index)

        markers = []
        markers.append(dtstamps)
        markers.append(dat)
        markers.append(strstamps)
        return markers  

    def anotateAxes(self,axes,s,rsdate,tmp,flare):
        """ Insert markers in plot """
        #twi = self.settwilight(rsdate) #regular 
        twi = flare
        endate = rsdate + timedelta(hours=23, minutes=59, seconds=59)

        if tmp:
            riseshade = tmp[0]
            setshade = tmp[1]
            axes.axvspan(rsdate, riseshade, facecolor='gray', alpha=0.5)
            axes.axvspan(setshade, endate, facecolor='gray', alpha=0.5)

        if twi:        
            xtwi = twi[0]   # datetime
            strtwi = twi[2] # label
            ttwi = []
            for t in twi[1]: # append raw data at index
                u = t.hour * 60 * 60
                u += t.minute * 60
                u += t.second
                u = u/5
                ttwi.append(s[(u)])
            
            axes.plot(xtwi, ttwi, color='red', marker='o', linestyle='None')
            for i in range(len(xtwi)):
                bboxparams=dict(boxstyle="round4,pad=0.2",fc='red',lw=0, alpha=0.5)
                axes.annotate(strtwi[i], (xtwi[i], ttwi[i]), color='white', size='20', bbox=bboxparams)
             

    def anotateflareAxes(self,axes,s,rsdate,endate,tmp,flare,region,con):
        """ Insert markers in plot """
        #tmp = self.settwishade(rsdate)
        if tmp:
            riseshade = tmp[0]
            setshade = tmp[1]
            axes.axvspan(rsdate, riseshade, facecolor='gray', alpha=0.5)
            axes.axvspan(setshade, endate, facecolor='gray', alpha=0.5)

        #flare = self.setflaremarks(rsdate)
        if flare:        
            begflare = flare[0]
            endflare = flare[1]
            strflare = flare[2]

            for i in range(len(begflare)):
                bboxparams=dict(boxstyle="round4,pad=0.2",fc='black',lw=0)
                axes.annotate(strflare[i], (begflare[i], 0), color='black', size=18)
                #axes.annotate(strflare[i], (begflare[i], 0.925e5*(i%2)+2e3), color='white', size=18, bbox=bboxparams)

        # indices
        st = region[:-1]
        ed = region[1:]
        ed = [ x + timedelta(seconds=-1) for x in ed]

        for st,ed,con in zip(st,ed,con):
            axes.axvspan(st, ed, facecolor=con, alpha=0.25)

    def draw5(self, rs, s, su, sstd, cu, cl, rx, rsdate,night,flare,region,con):
        """ RCL PLOT """         
        #2160  15120
        rs = numpy.asarray(rs)      # time
        sstd = numpy.asarray(sstd)  # std
        cu = numpy.asarray(cu)      # upper limit
        cl = numpy.asarray(cl)      # lower limit
        s =  numpy.asarray(s)       # marker time
        rx = numpy.asarray(rx)      # marker

        if True:
            # 2160 15120
            # 5400 6120
            beg = 6480
            end = 7920
            # beg = 0
            # end = 17280 - 1
            rs = rs[beg:end]
            sstd = sstd[beg:end]
            cu = cu[beg:end]
            cl = cl[beg:end]
            s = s[beg:end]
            rx = rx[beg:end]
            endate = rsdate + timedelta(seconds=end*5)
            rsdate = rsdate + timedelta(seconds=beg*5)
            
            

        self.axes1 = self.figure.add_subplot(313)
        #self.axes3 = self.figure.add_subplot(312)            
           
        # rolling mean at window
        #self.axes1.plot(rs, su)      
        #self.fmataxes(self.axes1)

        # # standard dev 
        self.axes1.plot(rs[1:], sstd[1:], label='Moving $\sigma$')
        self.axes1.legend()
        #self.axes1.set_ylim(0,2e7)

        self.axes2 = self.figure.add_subplot(211)
        # control limits
        lg1 = self.axes2.plot(rs[1:], cu[1:], color='mediumvioletred', linewidth=2, label='Upper Limit')
        lg2 = self.axes2.plot(rs[1:], cl[1:], color='palevioletred', linewidth=2, label='Lower Limit')            
        # points of intersections
        lg4 = self.axes2.plot(rs[1:], rx[1:], color='red', marker='8', linewidth=2, label='Detection')  

        # add points
        self.anotateflareAxes(self.axes2,s[1:],rsdate,endate,night,flare,region,con)

        # signal #s
        lg3 = self.axes2.plot(rs[1:], s[1:], color='darkgreen', linewidth=2, label='Signal')
        lds = lg1 + lg2 + lg3 + lg4
        lbls = [ l.get_label() for l in lds]

        font = font_m.FontProperties(size=20)
        self.axes2.legend(lds,lbls, prop=font)
        self.axes2.set_xlim(rsdate, endate)
        self.fmataxes(self.axes1)
        self.fmataxes(self.axes2)      


    def draw6(self, xray, xtime):
        """ Plot Xray """
        self.axes1 = self.figure.add_subplot(211)
        self.axes1.semilogy(xtime[1:], xray[1:], color='red', linewidth=2)
        self.axes1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.axes1.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
        self.axes1.set_xlabel("UTC Time")
        self.axes1.set_ylabel("Watts m^-2")
        self.axes1.set_ylim(pow(10,-6.5),pow(10,-2.5))

        dlg = wx.TextEntryDialog(self, 'Plot Title', 'Viewer')
        dlg.SetValue('GOES-13 SEP 6, 2017')
        if dlg.ShowModal() == wx.ID_OK:
            self.axes1.set_title(dlg.GetValue())

        #self.fmataxes(self.axes1)


    def draw7(self, freqs, ss1, ss2):
        """ Plot PSD """
        self.axes1 = self.figure.add_subplot(111)
        self.axes1.semilogy(freqs, ss1, color='blue', linewidth=2, label='Microcomputer')
        

        self.axes1.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        self.axes1.set_xlabel("Frequency")
        self.axes1.grid(b=True)
        self.axes1.set_ylabel('Relative Strength')

        #self.axes2 = self.axes1.twinx()
        self.axes1.semilogy(freqs, ss2, color='green', linewidth=2, label='Desktop')
        #self.axes2.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        #self.axes2.set_ylabel('(Desktop) Relative Strength')

        self.axes1.set_title('Power Spectral Density')
        self.axes1.axvline(freqs[211], color='red', linewidth=2, linestyle='dashed', label='NWC 19.8 kHz')
        self.axes1.axvline(freqs[237], color='magenta', linewidth=2, linestyle='dashed', label='NDT 22.2 kHz')
        self.axes1.legend(loc=1)


    def fmataxes(self, axes):
        axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        axes.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        axes.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
        axes.set_xlabel("UTC Time")

        # dlg = wx.TextEntryDialog(self, 'Y Lim Title', 'Viewer')
        # dlg.SetValue('Relative Strength')
        # if dlg.ShowModal() == wx.ID_OK:
        #     axes.set_ylabel(dlg.GetValue())

        # dlg = wx.TextEntryDialog(self, 'Plot Title', 'Viewer')
        # dlg.SetValue('AGO-GBZ SEP 6, 2017')
        # if dlg.ShowModal() == wx.ID_OK:
        #     axes.set_title(dlg.GetValue())
            

class SidViewer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #self._sid_path = "C:\\Users\\yenan\\Dropbox\\Sidbackup\\TEMP"
        self._sid_path = "C:\\Users\\yenan\\Dropbox\\Sidbackup\\TEST\\AGO-GQD"
        self._rfl_path = "C:\\Users\\yenan\\OneDrive - Mapua Institute of Technology\\COE200L - THESIS\\FINAL PAPER\\RainFall_2018.xlsx"
        #self._rfl_path = "C:\\Users\\yenan\\OneDrive - Mapua Institute of Technology\\COE200L - THESIS\\FINAL PAPER\\RainFall_Port Area Synop_2018.xlsx"
        self.dpath1 = []
        self.dpath2 = []

        self.dname1 = []
        self.dname2 = []

        self.sid1 = []
        self.sid2 = []

        self.rfal = []
        self.rsdate = None
        self.tstamp = []
        
        self.timestamp_format = "%Y-%m-%d %H:%M:%S"
        self.temp = '252,3.5'

        beg = (0, 0)
        edn = (23, 59)
        self.setmark()
        self.up = ((beg[0]*60) + beg[1])*12
        self.dn = ((edn[0]*60) + edn[1])*12
        

        #CONTROLS
        self.label1 = wx.StaticText(self, label="DIR 1:") 
        self.combo1 = wx.ComboBox(self, style=wx.CB_READONLY)
        self.buttn1 = wx.Button(self, wx.ID_ANY, '...')

        self.label2 = wx.StaticText(self, label="DIR 2:") 
        self.combo2 = wx.ComboBox(self, style=wx.CB_READONLY)
        self.buttn2 = wx.Button(self, wx.ID_ANY, '...') 

        self.buttn3 = wx.Button(self, wx.ID_ANY, 'Simple')
        self.buttn4 = wx.Button(self, wx.ID_ANY, 'Superimposed Rel')
        self.buttn5 = wx.Button(self, wx.ID_ANY, 'Rainfall Plot')   
        self.buttn6 = wx.Button(self, wx.ID_ANY, 'Enhanced')   
        self.buttn7 = wx.Button(self, wx.ID_ANY, 'Analyze')
        self.buttn8 = wx.Button(self, wx.ID_ANY, 'Xray')
        self.buttn9 = wx.Button(self, wx.ID_ANY, 'PSD')

        self.in1sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.in1sizer.Add(self.label1, 0, wx.ALL, 7 )
        self.in1sizer.Add(self.combo1, 1, wx.ALL|wx.EXPAND, 5)
        self.in1sizer.Add(self.buttn1, 0, wx.ALL|wx.EXPAND, 5)

        self.in2sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.in2sizer.Add(self.label2, 0, wx.ALL, 7 )
        self.in2sizer.Add(self.combo2, 1, wx.ALL|wx.EXPAND, 5)
        self.in2sizer.Add(self.buttn2, 0, wx.ALL|wx.EXPAND, 5)

        self.in4sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.in4sizer.Add(self.buttn3, 0, wx.ALL|wx.EXPAND, 5)
        self.in4sizer.Add(self.buttn8, 0, wx.ALL|wx.EXPAND, 5)
        self.in4sizer.Add(self.buttn4, 0, wx.ALL|wx.EXPAND, 5)
        self.in4sizer.Add(self.buttn5, 0, wx.ALL|wx.EXPAND, 5)
        self.in4sizer.Add(self.buttn6, 0, wx.ALL|wx.EXPAND, 5)
        self.in4sizer.Add(self.buttn7, 0, wx.ALL|wx.EXPAND, 5)
        self.in4sizer.Add(self.buttn9, 0, wx.ALL|wx.EXPAND, 5)
        
        
        self.labels1 = wx.StaticText(self, label="Slope: ")
        self.labels2 = wx.StaticText(self, label="P-val: ")
        self.labels3 = wx.StaticText(self, label="T-val: ")

        self.txtbox1 = wx.TextCtrl(self, -1, '', style=wx.TE_READONLY)        
        self.txtbox2 = wx.TextCtrl(self, -1, '', style=wx.TE_READONLY)
        self.txtbox3 = wx.TextCtrl(self, -1, '', style=wx.TE_READONLY)

        self.in3sizer = wx.BoxSizer(wx.HORIZONTAL)
                
        self.in3sizer.Add(self.labels1, 0, wx.ALL, 7)
        self.in3sizer.Add(self.txtbox1, 1, wx.ALL|wx.EXPAND, 5)
        self.in3sizer.Add(self.labels2, 0, wx.ALL, 7)
        self.in3sizer.Add(self.txtbox2, 1, wx.ALL|wx.EXPAND, 5)
        self.in3sizer.Add(self.labels3, 0, wx.ALL, 7)
        self.in3sizer.Add(self.txtbox3, 1, wx.ALL|wx.EXPAND, 5)
        
        #self.in3sizer.Add(self.buttn3, wx.ALL, 7)

        #PLOT
        self.figure = Figure()
        self.axes1 = self.figure.add_subplot(211)
        self.axes2 = self.figure.add_subplot(212)        
        #self.figure.tight_layout()

        self.canvas = FigureCanvas(self, -1, self.figure)        
        self.sizer = wx.BoxSizer(wx.VERTICAL)        
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

        #ALL TOGETHER
        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        self.topsizer.Add(self.in1sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.topsizer.Add(self.in2sizer, 0, wx.ALL|wx.EXPAND, 5)        
        self.topsizer.Add(self.in3sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.topsizer.Add(self.in4sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.topsizer.Add(self.sizer, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(self.topsizer)
        self.Fit()

        #BIND
        self.Bind(wx.EVT_BUTTON, self.pick1, self.buttn1)
        self.Bind(wx.EVT_BUTTON, self.pick2, self.buttn2)
        self.Bind(wx.EVT_BUTTON, self.pick3, self.buttn3)
        self.Bind(wx.EVT_BUTTON, self.pick4, self.buttn4)
        self.Bind(wx.EVT_BUTTON, self.pick5, self.buttn5)
        self.Bind(wx.EVT_BUTTON, self.pick6, self.buttn6)
        self.Bind(wx.EVT_BUTTON, self.pick7, self.buttn7)
        self.Bind(wx.EVT_BUTTON, self.pick8, self.buttn8)
        self.Bind(wx.EVT_BUTTON, self.pick9, self.buttn9)

        self.Bind(wx.EVT_COMBOBOX, self.oncombo1, self.combo1)
        self.Bind(wx.EVT_COMBOBOX, self.oncombo2, self.combo2)

        #STARTUP CONDITIONS
        sfpath = glob.glob(self._sid_path+"\\AGO_9190_GQD_2017-09*.txt") 
        sfname = []
        for infile in sfpath:
            sfname.append(infile.split("\\")[-1])
            self.combo1.Append(sfname[-1])
        self.dpath1 = sfpath
        self.dname1 = sfname        
        self.combo1.Selection = 0

        wb = xl.open_workbook(self._rfl_path)
        for sh in range(3):            
            #inData = [[wb.sheet_by_index(sh).cell_value(r, c) for r in range(2, wb.sheet_by_index(sh).nrows)] for c in range(1, wb.sheet_by_index(sh).ncols)]
            inCol = []
            for c in range(1, wb.sheet_by_index(sh).ncols):
                inRow = []
                for r in range(2, wb.sheet_by_index(sh).nrows):
                    temp = wb.sheet_by_index(sh).cell_value(r, c)
                    if temp == u'':
                        inRow.append(numpy.nan)
                    else:
                        inRow.append(temp)
                inCol.append(inRow)

            self.rfal.append(numpy.asarray(inCol))

    def filter(self, tsid, w=None):
        """ Filter the Data """

        if w:
            dlg = wx.TextEntryDialog(self, 'Smoothing window', 'Viewer')
            dlg.SetValue('240')

            if dlg.ShowModal() == wx.ID_OK:
                sfilter = int(dlg.GetValue())
            else:
                sfilter = 1 
        else:
            #sfilter = int(w*0.1)
            sfilter = 0

        if sfilter>1:
            tmp1 = []
                    
            for i in range(sfilter-1):
                tmp1.append(numpy.nan)

            for i in range(17280-sfilter+1):
                tmp1.append(numpy.median(tsid[1][(i):(i+sfilter)]))
            tsid[1] = tmp1

        return tsid


    def doStat(self, event):
        slope, intercept, r_value, _, _ = stats.linregress(self.sid1[1][self.up:self.dn], self.sid2[1][self.up:self.dn])
        
        self.slope = slope
        self.intercept = intercept
        self.r_value = r_value

        self.txtbox1.SetValue(str(slope))        
        self.txtbox2.SetValue(str(r_value))        

        t2, p2 = stats.ttest_ind(self.sid1[1], self.sid2[1])
        self.txtbox3.SetValue(str(t2)+', '+str(p2))

    def pick1(self, event):
        filedialog = wx.FileDialog(self, message = 'Choose files to plot', 
                                   defaultDir = self._sid_path, 
                                   defaultFile = '', 
                                   wildcard = 'Supported filetypes (*.csv, *.txt) |*.csv;*.txt', 
                                   style = wx.FD_OPEN | wx.FD_MULTIPLE) 

        if filedialog.ShowModal() == wx.ID_OK:   
            self.combo1.Clear()
            self.dpath1 = filedialog.GetPaths()
            self.dname1 = filedialog.GetFilenames()
            for infile in filedialog.GetFilenames():
                self.combo1.Append(infile)
            self.combo1.Selection = 0
        

    def pick2(self, event):
        filedialog = wx.FileDialog(self, message = 'Choose files to plot', 
                                   defaultDir = self._sid_path, 
                                   defaultFile = '', 
                                   wildcard = 'Supported filetypes (*.csv, *.txt) |*.csv;*.txt', 
                                   style = wx.FD_OPEN | wx.FD_MULTIPLE) 

        if filedialog.ShowModal() == wx.ID_OK:   
            self.combo2.Clear()
            self.dpath2 = filedialog.GetPaths()
            self.dname2 = filedialog.GetFilenames()
            for infile in filedialog.GetFilenames():
                self.combo2.Append(infile)
            self.combo2.Selection = 0

    def pick3(self, event):
        """ Simple Plot """
        if self.sid1:

            #sid1 = self.filter(list(self.sid1))
            sid1 = (self.sid1[0], numpy.asarray(self.lowpassfilt2(list(self.sid1[1]))))

            app = wx.App(False)
            fr = wx.Frame(None, title='Simple Plot', size=(800, 600))
            panel = SepViewer(fr)            

            panel.draw(sid1, self.rsdate, self.settwishade(), self.setflaremarks())
            fr.Show()
            app.MainLoop()


    def pick4(self, event):
        """ Plots sid1 and sid2 with relative y axis """
        if self.sid1 and self.sid2:

            sid1 = self.filter(list(self.sid1))
            sid2 = self.filter(list(self.sid2))

            app = wx.App(False)
            fr = wx.Frame(None, title='Relative Superimposed Plot', size=(800, 600))
            panel = SepViewer(fr)

            panel.draw2(self, sid1, sid2)
            fr.Show()
            app.MainLoop()

    def pick5(self, event):
        """ Plots Rainfall with sid1 """ 
        if self.sid1:

            sheet = self.rsdate.month - 6 # 5
            day = self.rsdate.day - 1
            rfal = self.rfal[sheet][day]
            xrfal = self.generate_timestamp(self.rsdate, 600) 

            sid1 = self.filter(list(self.sid1))

            app = wx.App(False)
            fr = wx.Frame(None, title='Rainfall Plot', size=(800, 600))
            panel = SepViewer(fr)

            panel.draw3(sid1, rfal, xrfal)
            fr.Show()
            app.MainLoop() 
            
    def pick6(self, event): 
        """ Derivative plot """
        if self.sid1:

            sid1 = self.filter(list(self.sid1))
            sid1 = numpy.asarray(sid1)

            ensid = []
            ensid = sid1[1][1:17280] - sid1[1][0:17279]
            ensid = numpy.concatenate([[numpy.nan], ensid])

            sid1[1] = ensid

            app = wx.App(False)
            fr = wx.Frame(None, title='Enhanced Plot', size=(800, 600))
            panel = SepViewer(fr)
            

            panel.draw4(sid1, self.rsdate, self.settwishade(), self.setflaremarks())
            fr.Show()
            app.MainLoop() 

    def timetoIndex(self,str):
        j = str.split(':')
        index = (int(j[0])*60*60) + int(j[1])*60
        index = (index/5) #- 1
        return index

    def setmark(self):
        # debug at sep 1 07:40 8:10
        # actual 4:40 18:11
        #4:40
        self.risestamps = ["4:40","04:42","04:44","04:46","04:48","04:50","04:52","04:54","04:56","04:58","05:00","05:02","05:04","05:06","05:08"]
        self.setstamps = ["18:11","18:09","18:07","18:05","18:03","18:01","17:59","17:57","17:55","17:53","17:51","17:49","17:47","17:45","17:43"]
        #18:11

        self.segment = 60
        # indices
        # self.region = [x for x in range(4320,12961,self.segment)]
        #self.st = self.region[:-1]
        #ed = self.region[1:]
        #self.ed = [x - 1 for x in ed]

        self.begflare = [
        ["15:37","17:14"],
        ["15:31"],
        [None],
        ["05:36","08:08","11:33","12:12","15:30","16:29","17:20"],
        #["06:33","10:13","12:30","13:26","16:14","17:11","17:37"],
        ["06:38","10:19","12:34","13:34","16:19","17:15","17:43"],

        #['06:22','07:34','09:10','12:02','15:56'],
        ["06:17","07:29","08:57","11:53","15:55"], 

        ["04:59","06:19","09:21","09:50","10:10","12:00","14:20"],
        ["05:31","06:24","06:35","07:08","07:44","09:35","10:50","11:21","12:13","12:29","15:24"],
        ["06:23","06:51","07:17","10:50","14:49","16:20"],
        ["09:02","14:19","15:23","15:35"],
        [None],
        ["07:29"],
        [None],
        [None],
        [None]]

        self.endflare = [
        ["15:41","17:19"],
        ["15:41"],
        [None],
        ["05:49","08:19","11:38","12:25","15:40","16:36","17:34"],
        ["06:48","10:25","12:39","13:41","16:22","17:21","17:51"],
        #["06:40","10:19","12:34","13:34","16:19","17:15","17:43"],

        ["06:22","07:34","09:10","12:02","16:01"],

        ["05:02","06:28","09:30","09:55","10:21","12:14","14:36"],
        ["05:36","06:27","06:41","07:18","07:51","09:41","11:00","11:27","12:23","12:33","15:32"],
        ["06:29","06:56","07:27","11:04","14:53","16:32"],
        ["09:20","14:23","15:26","15:55"],
        [None],
        ["07:39"],
        [None],
        [None],
        [None]]

        self.anotstamps = [
        ["C2.0","C1.2"],
        ["C7.7"],
        [""],
        ["M1.2","C2.9","C2.4","C8.3","M1.5","C4.1","C6.0"],
        ["M3.8","C5.4","C2.2","C6.9","C3.7","C4.6","M2.3"],
        ["C1.6","C2.7","X2.2","X9.3","M2.5"],
        ["M2.4","C8.2","C2.3","M1.4","M7.3","C3.0","X1.3"],
        ["C8.3","C2.9","C1.7","C6.0","M8.1","C1.3","C1.6","C1.7","C5.9","C1.2","M2.9"],
        ["C1.4","C1.7","C1.5","M3.7","C1.4","C1.7"],
        ["C2.9","C1.6","C1.0","X8.2"],
        [""],
        ["C3.0"],
        [""],
        [""],
        [""]]

    def setflaremarks(self):
        """ Set plot markers for flare """
        day = self.rsdate.day - 1
        if day > 14:
            return None
        
        begflare = self.begflare[day]
        endflare = self.endflare[day]
        anotstamps =  self.anotstamps[day]

        begstamps = []
        endstamps = []

        for beg, end in itertools.izip(begflare,endflare):            
            #dtstamps.append(datetime.strptime(temp_d+x, t_format))
            if beg and end:            
                j = beg.split(':')
                i = end.split(':')
                deltai = self.rsdate + timedelta(hours=int(j[0]),minutes=int(j[1]))
                deltaj = self.rsdate + timedelta(hours=int(i[0]),minutes=int(i[1]))
                begstamps.append(deltai)
                endstamps.append(deltaj)
            else:
                return []

        markers = []
        markers.append(begstamps) 
        markers.append(endstamps)
        markers.append(anotstamps) # label in plot
        return markers  

    def settwishade(self):
        """ Set shaded area for night time """
        day = self.rsdate.day - 1
        if day > 14:
            return None

        rise = self.risestamps[day]
        set =  self.setstamps[day]

        if rise and set:
            i = rise.split(':')
            j = set.split(':')
            deltai = self.rsdate + timedelta(hours=int(i[0]),minutes=int(i[1]))
            deltaj = self.rsdate + timedelta(hours=int(j[0]),minutes=int(j[1]))
            return (deltai,deltaj)
        else:
            return

    def checkreg(self, beg, end):
        if beg != [None]:
            ibeg = [self.timetoIndex(x) - (self.timetoIndex(x) % self.segment) for x in beg]
            iend = [self.timetoIndex(x) + (self.segment - (self.timetoIndex(x) % self.segment)) for x in end]
            return lambda x : [(x > b) and (x < e) for b,e in zip(ibeg, iend)]
        else:
            return lambda x : [False]

    def getclass(self, clist, fClass):
        if fClass != [""]:
            return fClass[clist.index(True)][0]
        else:
            return  ""
        
    def TPR(self,TP,FN):
        try:
            TPR = float(TP)/(TP+FN)
        except ZeroDivisionError:
            TPR = 0
        return TPR

    def FPR(self,FP,TN):
        return float(FP)/(FP+TN)

    def tallyclass(self, cond, fClass, tpfn, tally):
        # [[C],[M],[X],FP,TN]
        # [C] = (TP,FN)
        if fClass == 'X':
            if tpfn == 0:
                cond[2][0] += tally
            else:
                cond[2][1] += tally

        elif fClass == 'M':
            if tpfn == 0:
                cond[1][0] += tally
            else:
                cond[1][1] += tally

        elif fClass == 'C':
            if tpfn == 0:
                cond[0][0] += tally
            else:
                cond[0][1] += tally

    def lowpassfilt2(self,sig):
        alpha = 0.8
        out = [None]*len(sig)
        out[0] = sig[0]*alpha

        for i in range(1,len(sig)):
            out[i] = out[i-1] + alpha * (sig[i] - out[i-1])

        return out 

    @classmethod
    def filter_buffer(cls, raw_buffer, data_interval, bema_wing = 6, gmt_offset = 0):
            '''
            Return bema filtered version of the buffer, with optional time_zone_offset.
            bema filter uses the minimal found value to represent the data points within a range (bema_window)
            bema_wing = 6 => window = 13 (bema_wing + evaluating point + bema_wing)
            '''
            length = len(raw_buffer)
            # Extend 2 wings to the raw data buffer before taking min and average
            dstack = numpy.hstack((raw_buffer[length-bema_wing:length],
                                   raw_buffer[0:length],
                                   raw_buffer[0:bema_wing]))
            # Fill the 2 wings with the values at the edge
            dstack[0:bema_wing] = raw_buffer[0]  #  dstack[bema_wing]
            dstack[length+bema_wing:length+bema_wing*2] = raw_buffer[-1]  # dstack[length+bema_wing-1]
            # Use the lowest point found in window to represent its value
            dmin = numpy.zeros(len(dstack))
            for i in range(bema_wing, length+bema_wing):
                dmin[i] = min(dstack[i-bema_wing:i+bema_wing])
            # The points beyond the left edge, set to the starting point value
            dmin[0:bema_wing] = dmin[bema_wing]
            # The points beyond the right edge, set to the ending point value
            dmin[length+bema_wing:length+bema_wing*2] = dmin[length+bema_wing-1]
            # Moving Average. This actually truncates array to original size
            daverage = movavg(dmin, (bema_wing*2+1))

            if gmt_offset == 0:
                return daverage
            else:
                gmt_mark = gmt_offset * (60/data_interval) * 60
                doffset = numpy.hstack((daverage[gmt_mark:length],daverage[0:gmt_mark]))
                return doffset

    def pick7(self, event):
        """ Analysis using PCL """
        if self.sid1:
            # apply ewma
            # apply ewma for online capture

            day = self.rsdate.day - 1

            if day <= 15:
                isflare = self.checkreg(self.begflare[day], self.endflare[day])
                flareclass = self.anotstamps[day]
                
                rise = self.timetoIndex(self.risestamps[day])
                set =  self.timetoIndex(self.setstamps[day])

            else:
                isflare = lambda x : [False]
                flareclass = [None]
                rise = 0 
                set = 17280

            xrise = rise + (self.segment - (rise%self.segment))
            self.region = [self.rsdate + timedelta(minutes=x/12) for x in range(xrise,set,self.segment)]
            xregion = [x for x in range(rise,set,self.segment)]


            dlg = wx.TextEntryDialog(self, 'W in seconds, K_distance:', 'Viewer')
            dlg.SetValue(self.temp)
            
            if dlg.ShowModal() == wx.ID_OK:
                diagin = dlg.GetValue()

                if len(diagin) > 0:
                    cin = diagin.split(',')
                    self.temp = dlg.GetValue()
                    ns = int(cin[0])                            # window by element /5 if seconds
                    k = float(cin[1])
                    
                    if len(cin) > 2:
                        thresh = int(cin[2])
                    else:
                        thresh = 1

                    param = [[ns,k]]
                    verbose = True
                else:
                    aNs = range(60,361,12)                      # 5 min to 30 min 1 min increment
                    aK = [float(x)/10 for x in range(30,41,5)]  # 3.0 to 4.0 0.1 increment
                    param = []

                    for i in aNs:
                        for j in aK:
                            param.append([i,j])
                    verbose = False

                rs = []
                rs = self.generate_timestamp(self.rsdate, 5)    # timestamp           
                tsid = list(self.sid1)[1]
                #tsid =  self.filter(list(self.sid1),ns)[1]
                #tsid = numpy.asarray(self.lowpassfilt2(tsid))
                #tsid = self.filter_buffer(tsid,5)                
                #tsid = numpy.asarray(self.lowpassfilt2(tsid))

                for ns,k in param:
                    sstd = []   #standard dev
                    su = []     #rolling mean      
                    cu = []     #control upper
                    cl = []     #control lower
                    rx = []     #intersection

                    TP = TN = FP = FN = 0

                    CON = []    # saves values
                    
                    xhit = []   # debug
                    shit = []   # saves hit points of size segment
                    tally = [0] * 4  # tallies TP,FP,FN,TN

                    cond = [[0,0,'C'],[0,0,'M'],[0,0,'X']]

                    old = 0
                    dcount = 0    

                    for i in range(17280):

                        if i < ns:
                            sstd.append(0)
                            su.append(numpy.nan)
                            cl.append(numpy.nan)
                            cu.append(numpy.nan)
                            rx.append(numpy.nan)                           
                        else:
                            # array at index
                            sid = tsid[i]
                            # signal array within window
                            s = tsid[(i-ns):(i)]
                            s = self.lowpassfilt2(s)

                            # standard deviation
                            std = numpy.std(s)                    
                            sstd.append(std)
                            # sma
                            u = numpy.median(s)
                            su.append(u)
                            # limits
                            c = u + k*std #+ y*u
                            d = u - k*std #- y*u
                            if d < 0.0:
                                d = 0
                            cu.append(c)
                            cl.append(d)
                                                   
                            #thresh = 1

                            #j = i + ns - 1
                            j = i
                            hit = False

                            if (sid >= c or sid <= d) and (j >= rise and j <= set): # and dsum >= std:
                                dcount += 1 
                                if dcount > thresh:
                                    
                                    # print('{0}: {1:.2f}, {2:.2f}'.format(j,sid,std))
                                    
                                    rx.append(sid)                     
                                    old = i 
                                    hit = True                                
                                    shit.append(True) 
                                                                       
                                else:
                                    rx.append(numpy.nan)            
                                    shit.append(False)      

                            else:
                                rx.append(numpy.nan)
                                shit.append(False)

                                # if i - old == 1 and i > 1:
                                #     print('{0} \n'.format(dcount-thresh))

                                dcount = 0

                            shit = shit[-self.segment:]
                            xhit.append([hit,j])
                            xhit = xhit[-self.segment:]

                            if (j >= rise + self.segment and j <= set) and (j+1) % self.segment == 0:
                                clist = isflare(j)
                                if any(clist): # flare
                                    fClass = self.getclass(clist,flareclass)
                                    if any(shit): 
                                        # Treat the FN detection at the last region as TN
                                        if CON[-1] == 'y':
                                            CON[-1] = 'g'
                                            tally[3] += 1
                                            tally[1] -= 1
                                            self.tallyclass(cond,fClass,1,-1)

                                        # TP                                 
                                        CON.append('b')
                                        tally[0] += 1
                                        self.tallyclass(cond,fClass,0,1)

                                    else:
                                        # Treat no detection before detection as TP
                                        if len(CON) > 0 and CON[-1] == 'b':
                                            CON.append('b')
                                            tally[0] += 1
                                            self.tallyclass(cond,fClass,0,1)

                                        else:
                                        # FN
                                            CON.append('y')
                                            tally[1] += 1
                                            self.tallyclass(cond,fClass,1,1)
                                else: # no flare
                                    if any(shit):
                                        # Treat no detection after detection as TP
                                        if len(CON) > 0 and CON[-1] == 'b':
                                            CON.append('b')
                                            tally[0] += 1
                                            self.tallyclass(cond,fClass,0,1)

                                        else:
                                            # FP
                                            CON.append('r')
                                            tally[2] += 1
                                            # print('<<FP {0}>>'.format(j))
                                    else:
                                        # TN
                                        CON.append('g')
                                        tally[3] += 1
                                        
                                shit = []
                                xhit = []
                    
                    if verbose:
                        TP = tally[0]
                        FN = tally[1]
                        FP = tally[2]
                        TN = tally[3]

                        print("<<w = {0}, k = {1} - {2:%Y-%m-%d}>>\n".format(ns,k,self.rsdate))
                        print('SEGMENT TOTAL')            
                        print('TP = {0}, FN = {1}, FP = {2}, TN = {3}'.format(TP,FN,FP,TN))
                        print('TPR = {0:.2%}, FPR = {1:.2%}'.format(self.TPR(TP,FN),self.FPR(FP,TN)))
                        print('')

                    strcond = '{0:%Y-%m-%d}, {1}, {2}, '.format(self.rsdate,ns,k)

                    for f in cond:
                        TP = f[0]
                        FN = f[1]
                        
                        strcond += '{0}, {1}, {2:.5f}, '.format(TP, FN, self.TPR(TP,FN))

                        if (TP != 0 or FN != 0) and verbose:
                            print('{0} CLASS'.format(f[2]))
                            print('TP = {0}, FN = {1}, FP = {2}, TN = {3}'.format(TP,FN,FP,TN))
                            print('TPR = {0:.2%}, FPR = {1:.2%}\n'.format(self.TPR(TP,FN),self.FPR(FP,TN)))

                    if verbose:
                        s = tsid
                        pname = self.dname1[self.combo1.GetSelection()]
                    
                        app = wx.App(False)
                        fr = wx.Frame(None, title='w: {0}, k @ {1} - {2}'.format(ns, k, pname), size=(800, 600))
                        
                        panel = SepViewer(fr)
                        panel.draw5(rs, s, su, sstd, cu, cl, rx, self.rsdate, self.settwishade(), self.setflaremarks(), self.region, CON)
                        
                        fr.Maximize(True)
                        fr.Show()
                        app.MainLoop()
                    else:
                        TP = tally[0]
                        FN = tally[1]
                        strcond += '{0}, {1}, {2}, {3}, {4:.5f}, {5:.5f}'.format(TP,FN,FP,TN,self.TPR(TP,FN),self.FPR(FP,TN))
                        print(strcond)

            dlg.Destroy()

    def pick8(self, event):
        """ Plot GOES """
        t_format = "%Y-%m-%d"        
        str, xray = self.loadray(self.getsid())
        xray = sc.resample(xray, 17280)
        xtime = self.generate_timestamp(datetime.strptime(str, t_format), 5)

        app = wx.App(False)
        fr = wx.Frame(None, title='Enhanced Plot', size=(800, 600))
        panel = SepViewer(fr)

        panel.draw6(xray, xtime)
        fr.Show()
        app.MainLoop()

    def pick9(self, event):
        """ Plot PSD """
        freqs = []
        for i in range(513):
            freqs.append(i*93.75)

        ss1 = self.loadpsd(self.getsid())
        ss2 = self.loadpsd(self.getsid())

        app = wx.App(False)
        fr = wx.Frame(None, title='PSD Plot', size=(800, 600))
        panel = SepViewer(fr)

        panel.draw7(freqs, ss1, ss2)
        fr.Show()
        app.MainLoop()


    def oncombo1(self, event):        
        self.loadsid1(self.combo1.GetSelection())
        self.draw1()

        if self.sid1 and self.sid2:
            self.doStat(event)

    def oncombo2(self, event):
        self.loadsid2(self.combo2.GetSelection())
        self.draw2()

        if self.sid1 and self.sid2:
            self.doStat(event)


    def loadsid1(self, selcombo):
        fstr = self.dpath1[selcombo]
        self.sid1 = []        
        try:
            with open(fstr, "rt") as fin:
                lines = fin.readlines()
        except IOError:
                pass
        
        self.sid1.append(self.generate_timestamp(self.StrtoDate(lines[9]), 5))
        self.sid1.append(numpy.loadtxt(lines, dtype=float, comments='#', delimiter=",", usecols=(1, )).transpose())


    def loadsid2(self, selcombo):
        fstr = self.dpath2[selcombo]
        self.sid2 = []        
        try:
            with open(fstr, "rt") as fin:
                lines = fin.readlines()
        except IOError:
                pass
        self.sid2.append(self.generate_timestamp(self.StrtoDate(lines[9]), 5))
        self.sid2.append(numpy.loadtxt(lines, dtype=float, comments='#', delimiter=",", usecols=(1, )).transpose())

    def getsid(self):
        filedialog = wx.FileDialog(self, message = 'Choose files', 
                                   defaultDir = self._sid_path, 
                                   defaultFile = '', 
                                   wildcard = 'Supported filetypes (*.csv, *.txt) |*.csv;*.txt', 
                                   style = wx.FD_OPEN | wx.FD_MULTIPLE) 

        if filedialog.ShowModal() == wx.ID_OK:   
            return filedialog.GetPaths()

    def loadray(self, fstr):        
        ray = []        
        try:
            with open(fstr[0], 'rt') as fin:
                lines = fin.readlines()
        except Exception as e: 
                print(e)
                pass
        
        ray = numpy.loadtxt(lines, dtype=float, skiprows=140, delimiter=",", usecols=(6, )).transpose()
        return (lines[124].split(' ')[2].strip('"'), ray)

    def loadpsd(self, fstr):
        try:
            with open(fstr[0], 'rt') as fin:
                lines = fin.readlines()
        except Exception as e:
                print(e)
                pass
        return numpy.loadtxt(lines, dtype=float, comments='#', delimiter=",", usecols=(1, )).transpose()
        
    def generate_timestamp(self, startime, secs):
        """ Generate numpy datetime array """
        timestamp = numpy.empty(86400/secs, dtype=datetime)
        # add 'interval' seconds to UTC_StartTime for each entries
        interval =  timedelta(seconds=secs)        
        #currentTimestamp = self.StrtoDate(startime)
        for i in range(len(timestamp)):
            timestamp[i] =  startime
            startime += interval 

        return timestamp

    def StrtoDate(self, temp_d):
        """ Convert string to Datetime object """
        temp_d = temp_d.split('=', 1)[-1]
        temp_d = temp_d.lstrip(" ")
        temp_d = temp_d.rstrip("\n")
        dte = datetime.strptime(temp_d, self.timestamp_format)

        self.rsdate = dte
        return dte
       
    def draw1(self):
        self.axes1.clear()
        
        self.axes1.plot(self.sid1[0][self.up:self.dn], self.sid1[1][self.up:self.dn])
        self.fmataxes(self.axes1)
        self.canvas.draw()

    def draw2(self):
        self.axes2.clear()
        
        self.axes2.plot(self.sid2[0][self.up:self.dn], self.sid2[1][self.up:self.dn])
        self.fmataxes(self.axes2)
        self.canvas.draw()

    def fmataxes(self, axes):
        axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        axes.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        axes.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))

if __name__ == "__main__" :
    app = wx.App(False)
    fr = wx.Frame(None, title='MIT-PH SID Viewer', size=(800, 700))
    panel = SidViewer(fr) 
    fr.Show()
    app.MainLoop()
