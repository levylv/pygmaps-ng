def int2rgb(i):
    '''Turn integer into its three LSB and then turn that
    into a list of 0's and 255's'''
    return tuple([int(x)*255 for x in bin(i)[2:][:3].zfill(3)])


def gradient(n,start=(0,0,255),end=(255,255,255),overflow=(0,0,0)):
    '''
    returns a generator of hex colors that gradate from the 
    start color to the end color in n steps.  If overflow,
    after n colors overflow will be returned, if not
    overflow, the color cycle will repeat after n colors'''
    #red_step. green_step, blue_step:
    steps=[(end[i]-start[i])/(n-1) for i in range(3)]
    i = 0 # keeps track of what step we're on
    repeat = True
    while repeat:
      yield "#%02X%02X%02X" % tuple([start[j]+i*steps[j] for j in range(3)])
      i+=1
      if i == (n-1):
        yield "#%02X%02X%02X" % end
        if overflow:
          repeat=False
        else:
          i=0
    while True:
      yield "#%02X%02X%02X" % overflow
    
