static int mini_helper(int value)
{
    return value + 1;
}

int mini_add(int left, int right)
{
    if (left < 0) {
        return right;
    }
    return mini_helper(left) + right;
}

int mini_scale(int value)
{
    return value * 2;
}
