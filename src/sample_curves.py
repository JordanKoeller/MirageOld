# coding: utf-8

sc
get_ipython().run_line_magic('ls', '')
get_ipython().run_line_magic('cd', '../src/')
get_ipython().run_line_magic('ls', '')
from app.parameters.ExperimentParams import BatchLightCurveParameters
get_ipython().run_line_magic('ls', '')
get_ipython().run_line_magic('cd', '../debugging/')
get_ipython().run_line_magic('ls', '')
data = la.load('medium_radius.dat',0)
p = data.parameters
p.extras
oldcurve = p.extras['batch_lightcurve']
new = BatchLightCurveParameters(500,oldcurve.resolution/10,oldcurve.bounding_box)
new.resolution
qpts = new.lines[0]
qpts
len(qpts)
oldcurve.resolution
p.extras['batch_lightcurve'] = new
from app.lens_analysis.EngineDelegate import EngineDelegate
p.canvasDim
p.update(canvasDim=30000)
eng = EngineDelegate(p)
new.bounding_box.center
print(new.bounding_box.center)
eng.engine
print(new.bounding_box.center)
def getPlotOfTops(dataframe,tops,histogram=True):
         uniques_sorted = np.sort(dataframe['height'].unique())[::-1][0:tops]
         dfUniques = pd.DataFrame(uniques_sorted,columns=['height'])
         dataf2 = pd.merge(dfUniques,dataframe,on='height')
         stats = dataf2.groupby('radius').describe()
         mean = stats['abs_dif']['mean']/100
         stddev = stats['abs_dif']['std']/100
         x = np.linspace(5,40,20)
         if histogram:
             hist = dataf2.hist('abs_dif',by='radius',bins=50,sharex=True)
             plt.figure()
         plt.errorbar(x,mean,yerr=stddev,fmt='o')

         
def __slice_line(pts,bounding_box,resolution):
    #pts is an array of [x1,y1,x2,y2]
    #Bounding box is a MagMapParameters instance
    #resolution is a specification of angular separation per data point
    x1,y1,x2,y2 = pts
    m = (y2 - y1)/(x2 - x1)
    angle = math.atan(m)
    resolution = resolution.to('rad')
    dx = resolution.value*math.cos(angle)
    dy = resolution.value*math.sin(angle)
    dims = bounding_box.dimensions.to('rad')
    center = bounding_box.center.to('rad')
    lefX = center.x - dims.x/2
    rigX = center.x + dims.x/2
    topY = center.y + dims.y/2 
    botY = center.y - dims.y/2
    flag = True
    x = x1
    y = y1
    retx = [] 
    rety = [] 
    while flag:
        x -= dx
        y -= dy
        flag = x >= lefX and x <= rigX and y >= botY and y <= topY
    flag = True
    while flag:
        x += dx
        y += dy
        retx.append(x)
        rety.append(y)
        flag = x >= lefX and x <= rigX and y >= botY and y <= topY
    retx = retx[:-1]
    rety = rety[:-1]
    return [retx,rety]
c1 = new.lines[0]
c1
curve1 = __slice_line(c1,new.bounding_box,new.resolution)
curve1 = __slice_line(c1.value,new.bounding_box,new.resolution)
curve1
curve1 = np.array(curve1).T
curve1.shape
def sample_index(ind,retlist):
    tmp = []
    radii = u.Quantity(np.linspace(5,40,20),p.gravitationalRadius)
    curve = new.lines[ind]
    slc = __slice_line(curve.value,new.bounding_box,new.resolution)
    qpts = u.Quantity(np.array(slc).T,'rad')
    for r in radii:
        tmp.append(eng.query_line(qpts,r))
    retlist.append(tmp)
    
