function rmse = compute_rmse(GndImg, RecImg)
rmse = norm(GndImg - RecImg,'fro')/norm(GndImg,'fro');