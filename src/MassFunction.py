from scipy import stats
from astropy import units as u
import numpy as np
class MassFunction():
	def __init__(self,massDecay = None,alphas=[0.3,1.3,2.3],stepPoints=[0.08,0.5],resolution=200000):
		assert len(stepPoints)+1 is len(alphas), 'Error: There must be one more alpha then step point.'
		assert min(stepPoints)>0.01 and max(stepPoints)<120, 'Error: StepPoints must be bounded by 10^-2 and 10^2.'
		tmpLst = stepPoints
		stepPoints = [0.01] + stepPoints
		stepPoints.append(120)
		stepFunction = []
		for i in range(0,len(alphas)):
			stepFunction.append((stepPoints[i],stepPoints[i+1],alphas[i]))
		normalization = 0.0
		for i in stepFunction:
			normalization += self.__integrate(i[0],i[1],i[2])
		# print(normalization)
		x = (120-0.01)/resolution
		xk = []
		pk = []
		index = 0
		for i in range(0,resolution-1):
			xk.append(i)
			condition = True
			pkBuilder = 0
			while condition:
				integral = stepFunction[index]
				bottom = max(integral[0],i*x)
				top = min(integral[1],x*(i+1))
				pkBuilder += self.__integrate(bottom,top,integral[2])
				condition = top != x*(i+1)
				index += 1
			index -= 1
			pk.append(pkBuilder)
		pk = np.array(pk)
		pk /= sum(pk)
		self.generator = stats.rv_discrete(name='generator',values=(xk,pk),a=0.01,b=120)
		self.masses = np.arange(0.01,120,(120-0.01)/resolution)
		self.stepFunction = stepFunction



	def __integrate(self,low,high,alpha):
		return ((high**(1-alpha))/(1-alpha)-(low**(1-alpha))/(1-alpha))

	def query(self,num):
		lst = self.generator.rvs(size=num)
		ret = np.zeros(len(lst),dtype=np.float64)
		for i in range(0,len(lst)):
			ret[i] = self.masses[lst[i]]
		return ret

	def starField(self,mTot, tolerance):
		if mTot == 0:
			return []
		masses = self.query(mTot/0.83).tolist()
		massSum = sum(masses)
		while (abs(massSum-mTot)/mTot > tolerance):
			if massSum > mTot:
				masses.pop()
			else:
				masses += self.query(1).tolist()
			massSum = sum(masses)
		ret = u.Quantity(masses,'solMass')
		return ret

	def probFunction(self,x):
		for i in range(0,len(self.stepFunction)):
			if self.stepFunction[i][0] <= x and self.stepFunction[i][1] > x:
				return x**(-self.stepFunction[i][2])
		return 0
massGenerator = MassFunction()




