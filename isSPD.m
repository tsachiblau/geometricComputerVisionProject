function [S, PD] = isSPD(A)
    d = eig(A);
    PD = all(d) > 0;
    S = issymmetric(A);
end

