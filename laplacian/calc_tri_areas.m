function areas = calc_tri_areas(shape)
%calc_tri_areas Computes the area of each triangle

V1 = shape.VERT(shape.TRIV(:, 1), :);
V2 = shape.VERT(shape.TRIV(:, 2), :);
V3 = shape.VERT(shape.TRIV(:, 3), :);

V1 = V1 - V3;
V2 = V2 - V3;

% |cross(a, b)| = |a||b|sin(aplha)
areas = vecnorm(cross(V1, V2, 2), 2, 2) .* 0.5;
end
