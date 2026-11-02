import hexaly.optimizer as hx
print("version", hx.HxVersion.get_major_version_number(), hx.HxVersion.get_minor_version_number(), hx.HxVersion.get_build_date() if hasattr(hx.HxVersion,'get_build_date') else '')
with hx.HexalyOptimizer() as opt:
    m = opt.model
    x = m.int(0, 10); y = m.int(0, 10)
    m.constraint(x + y == 7)
    m.constraint(x - y >= 1)
    m.maximize(x * y)
    m.close()
    opt.param.time_limit = 5
    opt.param.verbosity = 0
    opt.solve()
    s = opt.solution
    print("status", s.status, "x", x.value, "y", y.value, "obj bound", s.get_objective_bound(0), "gap", s.get_objective_gap(0))
