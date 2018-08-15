from libc.math cimport sin, cos, atan2, sqrt ,atan, atanh, pi
from libcpp.pair cimport pair
from libcpp.vector cimport vector
from numpy cimport int32_t, float64_t


cdef pair[double,double] ray_trace(double &x,
    double &y,
    double &dL,
    double &dLS,
    double &dS,
    double &shear_mag,
    double &shear_angle,
    double &el_mag,
    double &el_angle,
    double &b) nogil:
    cdef double r, cosShear, sinShear, cosEl, sinEl, q1, res_x, res_y
    cdef double eex, eey, phi, ex, ey
    r = sqrt(x*x + y*y)
    cosShear = cos(-shear_angle)
    sinShear = sin(-shear_angle)
    cosEl = cos(el_angle)
    sinEl = sin(el_angle)
    q1 = sqrt(1.0 - el_mag*el_mag)
    #Elliptical SIS
    if r != 0.0:
        if el_mag == 1.0:
            res_x = x*b/r
            res_y = y*b/r
        else:
            eex = x*sinEl+y*cosEl
            eey = y*sinEl-x*cosEl
            ex = el_mag*b*atan(q1*eex/sqrt(el_mag*el_mag*eex*eex+eey*eey))/q1
            ey = el_mag*b*atanh(q1*eey/sqrt(el_mag*el_mag*eex*eex+eey*eey))/q1
            res_x = ex*sinEl-ey*cosEl
            res_y = ex*sinEl + ey*sinEl

    #shear
    phi = 2.0 * (pi/2.0 - shear_angle) - atan2(y,x)
    res_x += shear_mag*r*cos(phi)
    res_y += shear_mag*r*sin(phi)
    res_x = x - res_x
    res_y = y - res_y
    return pair[double,double](res_x,res_y)


cpdef int get_raw_magnification(object parameters,double radius):
    rayfield = parameters.rayfield
    quasar = parameters.quasar
    galaxy = parameters.galaxy
    cdef double ray_cx = rayfield.center.to('rad').x
    cdef double ray_cy = rayfield.center.to('rad').y
    cdef int counter = 0
    cdef double dx, dy, qx, qy
    cdef double dTheta_x = rayfield.dTheta.to('rad').x
    cdef double dTheta_y = rayfield.dTheta.to('rad').y
    cdef double dS = parameters.quasar.angDiamDist.to('lyr').value
    cdef double dL = parameters.galaxy.angDiamDist.to('lyr').value
    cdef double dLS = parameters.dLS.to('lyr').value
    cdef double shear_mag = parameters.galaxy.shear.magnitude
    cdef double shear_angle = parameters.galaxy.shear.angle.to('rad').value
    cdef double sis_constant = parameters.einstein_radius.to('rad').value
    cdef double el_mag = parameters.galaxy.ellipticity.magnitude
    cdef double el_angle = parameters.galaxy.ellipticity.angle.to('rad').value
    cdef double r2 = radius*radius
    cdef vector[pair[int32_t,int32_t]] check_pts
    cdef pair[double,double] source_pos
    cdef pair[double,double] center_pos = ray_trace(ray_cx,
                                            ray_cy,
                                            dL,
                                            dLS,
                                            dS,
                                            shear_mag,
                                            shear_angle,
                                            el_mag,
                                            el_angle,
                                            sis_constant)
    cdef int i, j
    cdef int ret = 0
    cdef int num = 0
    cdef int flag = 1
    cdef level = 0
    while flag == 1:
        flag = 0
        check_pts = vector[pair[int32_t,int32_t]]()
        index = 0
        for i in range(-level,level):
            if i == level or i == -level:
                for j in range(-level,level):
                    check_pts.push_back(pair[int32_t,int32_t](i,j))
            else:
                check_pts.push_back(pair[int32_t,int32_t](i,-level))
                check_pts.push_back(pair[int32_t,int32_t](i,level))
        for i in range(0,check_pts.size()):
            qx = ray_cx + check_pts[i].first*dTheta_x
            qy = ray_cy + check_pts[i].second*dTheta_y
            source_pos = ray_trace(qx,
                    qy,
                    dL,
                    dLS,
                    dS,
                    shear_mag,
                    shear_angle,
                    el_mag,
                    el_angle,
                    sis_constant)
            dx = source_pos.first - center_pos.first
            dy = source_pos.second - center_pos.second
            if dx*dx + dy*dy < r2:
                flag = 1
                num += ret
        level += 1
    return num


