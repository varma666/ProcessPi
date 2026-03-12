import processpi.equipment.heatexchangers.mechanical as mechanical
from processpi.equipment.heatexchangers.base import HeatExchanger


def test_run_mechanical_design_dispatches_double_pipe(monkeypatch):
    called = {}

    def fake_design(hx, **kwargs):
        called['hx'] = hx
        called['kwargs'] = kwargs
        return {'kind': 'double'}

    monkeypatch.setattr(mechanical, 'design_doublepipe', fake_design)
    monkeypatch.setitem(mechanical._design_type_map, 'DoublePipe', fake_design)

    hx = HeatExchanger(name='HX1')
    out = mechanical.run_mechanical_design(hx, type='DoublePipe', test_arg=1)

    assert out == {'kind': 'double'}
    assert called['hx'] is hx
    assert called['kwargs']['test_arg'] == 1


def test_run_mechanical_design_dispatches_shell_and_tube(monkeypatch):
    called = {}

    def fake_design(hx, **kwargs):
        called['hx'] = hx
        called['kwargs'] = kwargs
        return {'kind': 'shell'}

    monkeypatch.setattr(mechanical, 'design_shelltube', fake_design)
    monkeypatch.setitem(mechanical._design_type_map, 'ShellAndTube', fake_design)

    hx = HeatExchanger(name='HX2')
    out = mechanical.run_mechanical_design(hx, type='ShellAndTube', rating=True)

    assert out == {'kind': 'shell'}
    assert called['hx'] is hx
    assert called['kwargs']['rating'] is True


def test_run_mechanical_design_rejects_unknown_type():
    hx = HeatExchanger(name='HX3')

    try:
        mechanical.run_mechanical_design(hx, type='Unknown')
    except ValueError as exc:
        assert "Unknown type 'Unknown'" in str(exc)
    else:
        raise AssertionError('Expected ValueError for invalid type')
