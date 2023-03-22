import itertools
from decimal import Decimal

orderbook = {"symbol": "SOL-PERP", "bids": [[22.57, 8.85], [22.56, 88.54], [22.55, 177.08], [22.54, 23.65], [22.52, 1572.62], [22.51, 7.73], [22.18, 70.95], [22.14, 0.99], [21.59, 118.25], [21.34, 23.65], [20.0, 50.0], [19.5, 15.0], [18.5, 15.0], [17.59, 0.1], [17.59, 0.1], [17.59, 0.1], [17.0, 0.1], [15.09, 0.1], [12.59, 0.1]], "asks": [[22.6, 7.73], [22.61, 23.65], [22.61, 8.85], [22.63, 88.52], [22.64, 177.03], [22.66, 1486.55], [22.98, 70.95], [23.04, 1.54], [23.56, 118.25], [23.68, 21.11], [23.7, 200.0], [24.1, 0.6], [49.0, 0.1]], "slot": 183907411}

for side in {'bids', 'asks'}:
    orders = []

    for key, groups in itertools.groupby(orderbook.get(side, []), lambda order: order[0]):
        orders.append([key, float(sum([Decimal(str(size)) for price, size in groups]))])

    print(side, orders)
