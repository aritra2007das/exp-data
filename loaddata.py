#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import sys, yaml, re

class point:
	__slots__ = ['xl', 'x', 'xh', 'yl', 'y', 'yh', 'syslist', 'stat']
	def __init__(self, iv, dv):
		if 'value' in iv.keys():
			if type(iv['value']) == str:
				nl = re.split(' |,', iv['value'])
				self.x, pos, neg = float(nl[0]), float(nl[1]), float(nl[2])
				self.xl, self.xh = self.x+neg, self.x+pos
			else:		
				self.xl = iv['low']
				self.xh = iv['high']
				self.x = iv['value']	
		else:
			self.xl = iv['low']
			self.xh = iv['high']
			self.x = (self.xl + self.xh)/2.
		self.y = dv['value']
		self.syslist = []
		for item in dv['errors']:
			print (item)
			if 'stat' in item['label']:
				self.stat = [-item['symerror'], item['symerror']]
			if 'sys' in item['label']:
				if item.get('asymerror'):
					self.syslist.append([item['asymerror']['minus'],item['asymerror']['plus']])
				if item.get('symerror'):
					if type(item.get('symerror')) != str:
						self.syslist.append([-item['symerror'],item['symerror']])
					else:
						err = item['symerror']
						if err[-1] == '%':
							self.syslist.append([
							-self.y*float(err[:-1])/100.,
							self.y*float(err[:-1])/100.])
		self.yl = self.y + np.min([it[0] for it in self.syslist]+[self.stat[0]])
		self.yh = self.y + np.max([it[1] for it in self.syslist]+[self.stat[1]])
		
class plot_info:
	__slots__ = ['plist', 'xlabel', 'ylabel', 'description', 'ylog', 'x', 'y', 'prange']	
	def __init__(self, fin):
		with open(fin,'r') as f:    
			ds = yaml.load(f)
			# unpack x:
			iv = ds['independent_variables'][0]
			xname = iv['header']['name']
			xunit = iv['header'].get('units','')
			# unpack y:
			dv = ds['dependent_variables'][0]
			yname = dv['header']['name']
			yunit = dv['header'].get('units','')
			# fig description
			self.description = ''
			for it in dv['qualifiers']:
				self.description += it.get('name')+'='+it.get('value') + it.get('unit','') + '\n'
			# point data
			self.plist = [point(iiv, idv) for iiv, idv in zip(iv['values'], dv['values'])]
			# ploting label
			self.xlabel = xname+'['+xunit+']'
			self.ylabel = yname+'['+yunit+']'
			# determine plotting ranges and scale
			self.x = np.array([p.x for p in self.plist])
			self.y = np.array([p.y for p in self.plist])
			self.ylog = False
			xH = np.max([p.xh for p in self.plist])
			xL = np.min([p.xl for p in self.plist])
			yH = np.max([p.yh for p in self.plist])
			yL = np.min([p.yl for p in self.plist])
			if yL>0. and np.log10(yH/yL) > 2:
				self.ylog = True
			Lx = xH - xL
			Ly = yH - yL
			xmin = np.min([0., xL-Lx*0.1]) 
			xmax = xH+Lx*0.1
			ymin = np.min([0., yL-Ly*0.2]) if not self.ylog else 0.1*yL
			ymax = yH+Ly*0.2 if not self.ylog else 10*yH
			self.prange = [xmin, xmax, ymin, ymax]
	# recommand scale: normal / log
	def recommand_scale(self, ax, user=None, auto_log=True):
		if user == None:
			ax.axis(self.prange)
		else:
			ax.axis(user)
		if self.ylog and auto_log:
			ax.semilogy()

def main():
	pi = plot_info(sys.argv[1])
	f, ax = plt.subplots(1,1)
	color = ['r','g','b','y']
	alpha = [0.2, 0.3, 0.4, 0.5]
	for p in pi.plist:
		ax.errorbar(p.x, p.y,[[-p.stat[0]], [p.stat[1]]], fmt='rD', markersize=5)
		for it, c, a in zip(p.syslist, color, alpha):
			ax.fill_between([p.xl, p.xh], [p.y+it[0], p.y+it[0]],  [p.y+it[1], p.y+it[1]], alpha=a, color=c)
	ax.set_xlabel(pi.xlabel)
	ax.set_ylabel(pi.ylabel)
	box = AnchoredText(pi.description, loc=1, frameon=False)
	ax.add_artist(box)
	pi.recommand_scale(ax)
	plt.show()

if __name__ == "__main__":
    main()

