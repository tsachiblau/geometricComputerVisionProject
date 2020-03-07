function [v] = getOracleV(X, Y)
    
    D = pdist2(X.VERT, Y.VERT);   
    I = D < 1e-1;
    SI = sum(I, 2);
    v = SI < 1;
    v = double(v);
end

