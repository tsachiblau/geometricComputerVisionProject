function [distance_on_grapha, G] = calcGeodesicDistances(X)
    
    A = squareform(pdist(X.VERT));
    adgency_matrix = zeros(X.n, X.n);

    for i = 1 : X.m
        adgency_matrix(X.TRIV(i, 1), X.TRIV(i, 2)) = 1;
        adgency_matrix(X.TRIV(i, 2), X.TRIV(i, 3)) = 1;
        adgency_matrix(X.TRIV(i, 3), X.TRIV(i, 1)) = 1;
    end
    
    adgency_matrix = ((adgency_matrix>0) & (adgency_matrix' > 0)) >= 1;
    
    A(~adgency_matrix) = 0;
    %
    G = graph(A);
    x = X.VERT(:, 1);
    y = X.VERT(:, 2);
    z = X.VERT(:, 3);
    cmap = jet(size(X.VERT,1));
    
    figure();
    p = plot(G, 'XData', x, 'YData', y, 'ZData', z);
    p.NodeColor = cmap;

%     figure(); plot(G);
    distance_on_grapha = distances(G);

end

