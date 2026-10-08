from datetime import date
from django.db.models import Sum, Count, F
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sales.models import Sale
from products.models import Product
from inventory.models import Inventory
from forecasts.models import Forecast


def _get_shop(user):
    try:
        return user.shop
    except Exception:
        return None


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop = _get_shop(request.user)
        if not shop:
            return Response({'error': 'No shop linked to your account.'}, status=400)

        today = date.today()
        current_year = today.year
        prev_year = current_year - 1

        qs = Sale.objects.filter(shop=shop)

        # ── Totals ──
        totals = qs.aggregate(
            total_revenue=Sum('total_sales'),
            total_units=Sum('quantity'),
            total_profit=Sum('profit'),
        )

        # ── Year splits ──
        prev_year_qs = qs.filter(date__year=prev_year)
        curr_year_qs = qs.filter(date__year=current_year)

        prev_revenue = prev_year_qs.aggregate(r=Sum('total_sales'))['r'] or 0
        curr_revenue = curr_year_qs.aggregate(r=Sum('total_sales'))['r'] or 0
        prev_units   = prev_year_qs.aggregate(u=Sum('quantity'))['u'] or 0
        curr_units   = curr_year_qs.aggregate(u=Sum('quantity'))['u'] or 0

        revenue_growth = 0
        if prev_revenue > 0:
            revenue_growth = round(((curr_revenue - prev_revenue) / prev_revenue) * 100, 1)

        # ── Monthly sales (current year) ──
        monthly = list(
            curr_year_qs.values('month')
            .annotate(units=Sum('quantity'), revenue=Sum('total_sales'))
            .order_by('month')
        )

        # ── Top products ──
        top_products = list(
            qs.values('product__id', 'product__name', 'product__category', 'product__brand')
            .annotate(units=Sum('quantity'), revenue=Sum('total_sales'))
            .order_by('-units')[:10]
        )
        for p in top_products:
            p['product_id']   = p.pop('product__id')
            p['product_name'] = p.pop('product__name')
            p['category']     = p.pop('product__category')
            p['brand']        = p.pop('product__brand')

        # ── Heatmap: top 6 products × day_of_week ──
        top6_ids = [p['product_id'] for p in top_products[:6]]
        dow_rows = list(
            qs.filter(product_id__in=top6_ids)
            .values('product__id', 'product__name', 'day_of_week')
            .annotate(units=Sum('quantity'))
            .order_by('product__id', 'day_of_week')
        )
        # Build heatmap dict: {product_id: {dow: units}}
        heatmap_raw = {}
        for row in dow_rows:
            pid  = row['product__id']
            pname = row['product__name']
            dow  = row['day_of_week']  # 0=Mon … 6=Sun
            if pid not in heatmap_raw:
                heatmap_raw[pid] = {'name': pname, 'days': {}}
            heatmap_raw[pid]['days'][dow] = round(row['units'] or 0, 0)
        heatmap_data = [
            {
                'product_name': v['name'],
                'days': [v['days'].get(d, 0) for d in range(7)],
            }
            for v in heatmap_raw.values()
        ]

        # ── Current stock ──
        stock_total = Inventory.objects.filter(shop=shop).aggregate(
            s=Sum('current_stock')
        )['s'] or 0

        reorder_alerts = Inventory.objects.filter(
            shop=shop, current_stock__lte=F('reorder_point')
        ).count()

        # ── Next month forecast ──
        # Use the earliest available forecast month if next-month has no data
        all_forecasts = Forecast.objects.filter(shop=shop)
        first_forecast = all_forecasts.order_by('forecast_date').first()
        if first_forecast:
            f_month = first_forecast.forecast_date.month
            f_year  = first_forecast.forecast_date.year
            forecast_qs = Forecast.objects.filter(
                shop=shop,
                forecast_date__year=f_year,
                forecast_date__month=f_month,
            )
        else:
            forecast_qs = Forecast.objects.none()
        predicted_units   = forecast_qs.aggregate(s=Sum('predicted_qty'))['s'] or 0
        predicted_revenue = 0
        for f in forecast_qs.select_related('product'):
            predicted_revenue += f.predicted_qty * (f.product.unit_price or 0)

        # ── High demand products (top 10 by total predicted qty) ──
        from django.db.models import Sum as _Sum
        from forecasts.models import Forecast as _Forecast, ModelEvaluation as _ModelEval

        high_demand = list(
            _Forecast.objects.filter(shop=shop)
            .values('product__id', 'product__name', 'product__category', 'product__brand', 'product__unit_price')
            .annotate(predicted_total=_Sum('predicted_qty'))
            .order_by('-predicted_total')[:10]
        )
        for h in high_demand:
            h['product_id']   = h.pop('product__id')
            h['product_name'] = h.pop('product__name')
            h['category']     = h.pop('product__category')
            h['brand']        = h.pop('product__brand')
            h['unit_price']   = h.pop('product__unit_price')
            h['predicted_total'] = round(h['predicted_total'] or 0, 0)

        # ── Model accuracy (all evaluations for this shop) ──
        model_accuracy = list(
            _ModelEval.objects.filter(shop=shop)
            .select_related('product')
            .values('product__name', 'product__category', 'model_type', 'mae', 'mse', 'rmse', 'r2')
            .order_by('rmse')
        )
        for m in model_accuracy:
            m['product_name'] = m.pop('product__name')
            m['category']     = m.pop('product__category')
            m['mae']  = round(m['mae'],  4)
            m['mse']  = round(m['mse'],  4)
            m['rmse'] = round(m['rmse'], 4)
            m['r2']   = round(m['r2'],   4)

        # ── Recent sales ──
        recent = list(
            qs.select_related('product')
            .order_by('-date', '-id')[:10]
            .values('product__name', 'product__category', 'date', 'quantity', 'total_sales')
        )
        for r in recent:
            r['product_name'] = r.pop('product__name')
            r['category']     = r.pop('product__category')
            r['date']         = str(r['date'])

        return Response({
            'shop': {
                'id': shop.id,
                'name': shop.name,
                'location': shop.location,
                'category': shop.category,
                'owner': request.user.get_full_name() or request.user.username,
            },
            'total_revenue':    round(totals['total_revenue'] or 0, 2),
            'total_units':      round(totals['total_units'] or 0, 0),
            'total_profit':     round(totals['total_profit'] or 0, 2),
            'total_products':   Product.objects.filter(shop=shop).count(),
            'current_stock':    round(stock_total, 0),
            'reorder_alerts':   reorder_alerts,
            'prev_year_revenue': round(prev_revenue, 2),
            'curr_year_revenue': round(curr_revenue, 2),
            'prev_year_units':   round(prev_units, 0),
            'curr_year_units':   round(curr_units, 0),
            'revenue_growth':    revenue_growth,
            'monthly_sales':     monthly,
            'top_products':      top_products,
            'predicted_next_month_units':   round(predicted_units, 0),
            'predicted_next_month_revenue': round(predicted_revenue, 2),
            'forecast_month': first_forecast.forecast_date.strftime('%B %Y') if first_forecast else '',
            'recent_sales':        recent,
            'high_demand_products': high_demand,
            'model_accuracy':       model_accuracy,
            'heatmap_data':         heatmap_data,
        })
