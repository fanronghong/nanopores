function [sparse_point,sparse_weight] = test_sgmga(type,dim_num,itest,level_max,plotyn)

tol = sqrt(eps);
% spatial dimensions
% dim_num = 2;
% itest = [1;1];
% level_max = 2;

% anisotropy (see description in sgmga_importance_to_aniso.m)
importance = zeros(dim_num,1);
for dim = 1 : dim_num
    importance(dim,1) = itest(dim);
end
level_weight = sgmga_importance_to_aniso ( dim_num, importance );
%level_weigth = [1;1];
% different level_max values, level_max controls size of final grid


% rule used for grid generation in each dimension
if length(type) == 1
rule = type*ones(dim_num,1); % 1 = CC, 3 = GP, 4 = GL
else
    rule = type;
end

% growth rule in each dimension
growth = 6*ones(dim_num,1); % 6 = FE, 4 = SE, 5 = ME

% number of parameters for the rules in each dimension (= 0 for CC and
% GP)
np = zeros(dim_num,1);
np_sum = sum ( np(1:dim_num) );

% parameters (= 0 if np(dim_num) = 0)
p = zeros(np_sum,1);

% the total number of points in the grid.
point_total_num = sgmga_size_total ( dim_num, level_weight, level_max, ...
    rule, growth );

% the number of unique points in the grid.
point_num = sgmga_size ( dim_num, level_weight, level_max, rule, growth, ...
    np, p, tol );

%  lists, for each (nonunique) point, the corresponding index of the same
%  point in the unique listing.
sparse_unique_index = sgmga_unique_index ( dim_num, level_weight, ...
    level_max, rule, growth, np, p, tol, point_num, point_total_num );

%    Output, integer SPARSE_ORDER(DIM_NUM,POINT_NUM), lists,
%    for each point, the order of the 1D rules used in the grid that
%    generated it.
%
%    Output, integer SPARSE_INDEX(DIM_NUM,POINT_NUM), lists, for
%    each point, its index in each of the 1D rules in the grid that generated
%    it.  The indices are 1-based.
%    For each "unique" point in the sparse grid, we return its INDEX and ORDER.
%
%    That is, for the I-th unique point P, we determine the product grid which
%    first generated this point, and we return in SPARSE_ORDER the orders of
%    the 1D rules in that grid, and in SPARSE_INDEX the component indexes in
%    those rules that generated this specific point.
%
%    For instance, say P was first generated by a rule which was a 3D product
%    of a 9th order CC rule and a 15th order GL rule, and that to generate P,
%    we used the 7-th point of the CC rule and the 3rd point of the GL rule.
%    Then the SPARSE_ORDER information would be (9,15) and the SPARSE_INDEX
%    information would be (7,3).  This, combined with the information in RULE,
%    is enough to regenerate the value of P.


[ sparse_order, sparse_index ] = sgmga_index ( dim_num, level_weight, ...
    level_max, rule, growth, point_num, point_total_num, sparse_unique_index );

% grid points
sparse_point = sgmga_point ( dim_num, level_weight, level_max, rule, ...
    growth, np, p, point_num, sparse_order, sparse_index );
% and corresponding weights
sparse_weight = sgmga_weight ( dim_num, level_weight, level_max, ...
  rule, growth, np, p, point_num, point_total_num, sparse_unique_index )';

if plotyn
    figure
    if dim == 1
        plot(sparse_point(1,:),zeros(size(sparse_point(1,:))),'b*')
    end
    if dim ==2
        plot(sparse_point(1,:),sparse_point(2,:),'b*')
    end
    if dim ==3
        plot3(sparse_point(1,:),sparse_point(2,:),sparse_point(3,:),'b*')
    end
    axis square

%     ruleStr = {'CC ','F2 ','GP ','GL ','GH ','GGH','LG ','GLG','GJ ','HGK','UO ','UC '};
%     growthStr = {'DF','SL','SO','ML','SE','ME','FE'};
%     title(['rules = ',[ruleStr{rule}],', ',sprintf('level = %0.2f %0.2f',itest(1),itest(2)),', #points  = ',num2str(size(sparse_point,2))])
%     xlabel('x (molecule shift)')
%     ylabel('\phi (molecule angle)')
% %     dim_num, level_weight, level_max, rule, growth, np, p, point_num, sparse_order, sparse_index
%     numVal = [dim_num, level_weight, level_max, rule, growth, np, p, point_num, sparse_order, sparse_index]
%     formatSpec = 'dim_num = %1.0f, level_weight = %1.0f, level_max = %1.0f, rule = %1.0f, growth = %1.0f, np = %1.0f, p = %1.0f, point_num = %1.0f, sparse_order = %1.0f, sparse_index = %1.0f\n';
%     titleStr = sprintf(formatSpec,numVal);
%     title(titleStr)
%
%     fprintf ( 1, '\n' );
%     fprintf ( 1, '  For LEVEL_MAX = %d\n', level_max );
%     fprintf ( 1, '\n' );
%     for point = 1 : point_num
%       fprintf ( 1, '  %4d', point );
%       for dim = 1 : dim_num
%          fprintf ( 1, '  %14e', sparse_point(dim,point) );
%       end
%       fprintf ( 1, '\n' );
%     end

end
end
