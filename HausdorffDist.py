import numpy as np
import math as mt
import matplotlib.pyplot as plt


def HausdorffDist(P=None, Q=None, dv=None):
    # p: standard, Q: measured
    sP = P.shape
    sQ = Q.shape
    if not (sP[1] == sQ[1]):
        raise Exception('Inputs P and Q must have the same number of columns')
    # interpolation for measured data
    ssd = Q.shape
    Q_inter = np.array([Q[0]])
    # Q_inter = np.zeros((1, 2))
    # interpolation among sparse points
    if ssd[0] > 1 and ssd[1] == 2:
        max_inter = 3
        pad_idx = 0
        for i in range(1, ssd[0] - 1):
            pad_num = 1
            pad_idx = pad_idx + 1
            Q_inter = np.append(Q_inter, [Q[i]], axis=0)  # Q_inter[pad_idx, :] = Q[i, :]
            inter = np.sqrt(sum((Q[i] - Q[i + 1]) ** 2))
            while inter > pad_num * max_inter:
                pad_num = pad_num + 1
                pad_idx = pad_idx + 1
                Q_inter = np.append(
                    Q_inter, [Q_inter[pad_idx - 1] + (Q[i + 1] - Q[i]) * max_inter / inter],
                    axis=0)
                # Q_inter[pad_idx, :] = Q_inter[pad_idx - 1, :] + (Q[i + 1, :] - Q[i, :]) * max_inter /
                # inter
        Q_inter = np.append(Q_inter, [Q[-1]], axis=0)
    sQ = Q_inter.shape
    mp = np.zeros((sP[0], 1))
    ixp = np.ones((sP[0], 1))
    for i in range(0, sP[0]):
        mp[i] = 10000000000.0
        for j in range(0, sQ[0]):
            dist = np.sqrt(sum((Q_inter[j, :] - P[i, :]) ** 2))
            if mp[i] > dist:
                mp[i] = dist
                ixp[i] = j

    mq = np.zeros((sQ[0], 1))
    ixq = np.ones((sQ[0], 1))
    for i in range(0, sQ[0]):
        mq[i] = 10000000000.0
        for j in range(0, sP[0]):
            dist = np.sqrt(sum((Q_inter[i, :] - P[j, :]) ** 2))
            if mq[i] > dist:
                mq[i] = dist
                ixq[i] = j

    vp = np.mean(mp)

    vq = np.mean(mq)

    mhd = max(vp, vq)
    maxp = np.amax(mp)
    # maxp, ixpp = np.amax(mp)
    maxq = np.amax(mq)
    # maxq, ixqq = np.amax(mq)
    hd = np.amax(np.array([maxq, maxp]))
    ##
    # -- plot data --
    #
    # if P is not None and Q is not None and dv is not None and (
    #         dv in ['v', 'vis', 'visual', 'visualize', 'visualization']):
    #     pass
    # figure
    # # subplot(1,2,1)
    # hold('on')
    # plt.axis('equal')
    # h[1] = plt.plot(P(:,1),P(:,2),'bx','markersize',10,'linewidth',3)
    # h[2] = plt.plot(Q(:,1),Q(:,2),'ro','markersize',8,'linewidth',2.5)
    # Xp = np.array([P(np.arange(1,sP(1)+1),1),Q(ixp,1)])
    # Yp = np.array([P(np.arange(1,sP(1)+1),2),Q(ixp,2)])
    # plt.plot(np.transpose(Xp),np.transpose(Yp),'-b')
    # Xq = np.array([P(ixq,1),Q(np.arange(1,sQ(1)+1),1)])
    # Yq = np.array([P(ixq,2),Q(np.arange(1,sQ(1)+1),2)])
    # plt.plot(np.transpose(Xq),np.transpose(Yq),'-r')
    # if ix == 2:
    #     ixhd = np.array([ixp(ixpp),ixpp])
    #     xyf = np.array([[Q(ixhd(1),:)],[P(ixhd(2),:)]])
    # else:
    #     ixhd = np.array([ixqq,ixq(ixqq)])
    #     xyf = np.array([[Q(ixhd(1),:)],[P(ixhd(2),:)]])
    # h[3] = plt.plot(xyf(:,1),xyf(:,2),'-ks','markersize',12,'linewidth',2)
    # uistack(fliplr(h),'top')
    # plt.xlabel('East (m)')
    # plt.ylabel('North (m)')
    # plt.title(np.array([[np.array(['Max Distance = ',num2str(hd)])],[np.array(['Mean Distance = ',num2str(mhd)])],[[]]]))
    # plt.legend(h,np.array(['P','Q','Maximum Dist']),'location','eastoutside')

    return hd, mhd
