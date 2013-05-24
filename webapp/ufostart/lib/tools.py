def group_by_n(array, n=2):
    total = len(array)
    return [array[k*n:(k+1)*n] for k in range(total/n+1) if k*n<total]
