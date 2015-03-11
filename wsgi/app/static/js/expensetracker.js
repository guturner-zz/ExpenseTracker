function createExpenseChart(id, paramMap) {
    return Morris.Donut({
      element: id,
      data: paramMap
    });
}