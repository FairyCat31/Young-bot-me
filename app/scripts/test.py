

def test_const():
    def test_func():
        print("ok")

    return test_func


test = test_const()

test()