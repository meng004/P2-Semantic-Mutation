from p2.avp.interface import AVPResult, AVPInterface


def test_avp_result_is_pass_or_fail():
    assert AVPResult.PASS.value == "pass"
    assert AVPResult.FAIL.value == "fail"


def test_avp_interface_is_protocol():
    import typing
    assert hasattr(AVPInterface, "__class_getitem__")
