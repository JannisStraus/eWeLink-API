def assert_credentials(testcase, payload):
    testcase.assertIsInstance(payload, dict)
    testcase.assertIsInstance(payload.get("at"), str)
    testcase.assertIsInstance(payload.get("user", {}).get("email"), str)
    testcase.assertIsInstance(payload.get("region"), str)


def assert_all_device_shape(testcase, payload):
    testcase.assertIsInstance(payload.get("name"), str)
    testcase.assertIsInstance(payload.get("deviceid"), str)
    testcase.assertIsInstance(payload.get("apikey"), str)
    testcase.assertIsInstance(payload.get("params"), dict)
    testcase.assertIsInstance(payload.get("showBrand"), bool)
    testcase.assertIsInstance(payload.get("extra", {}).get("extra", {}).get("model"), str)


def assert_specific_device_shape(testcase, payload):
    testcase.assertIsInstance(payload.get("name"), str)
    testcase.assertIsInstance(payload.get("deviceid"), str)
    testcase.assertIsInstance(payload.get("apikey"), str)
    testcase.assertIsInstance(payload.get("online"), bool)
    testcase.assertIsInstance(payload.get("extra", {}).get("extra", {}).get("model"), str)


def assert_firmware_shape(testcase, payload):
    testcase.assertIsInstance(payload.get("status"), str)
    testcase.assertIsInstance(payload.get("deviceId"), str)
    testcase.assertIsInstance(payload.get("msg"), str)
