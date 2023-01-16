package rf.talyzin.neuro_invest_android

import android.graphics.*
import android.os.Bundle
import android.widget.Button
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.max
import kotlin.math.min


class FormPair : AppCompatActivity()
{
    private val graph by lazy { findViewById<ImageView>(R.id.graph) }
    private val refresh by lazy { findViewById<Button>(R.id.refresh) }
    private val close by lazy { findViewById<Button>(R.id.close) }

    private val borderPaint by lazy()
    {
        val form = this
        Paint().apply()
        {
            color = ContextCompat.getColor(form, R.color.black)
            style = Paint.Style.STROKE
            strokeWidth = 1.0f
        }
    }

    private val valuesPaint by lazy()
    {
        val form = this
        Paint().apply()
        {
            color = ContextCompat.getColor(form, R.color.values)
            style = Paint.Style.STROKE
            strokeWidth = 8.0f
        }
    }

    private val valuesCircle by lazy()
    {
        val form = this
        Paint().apply()
        {
            color = ContextCompat.getColor(form, R.color.values)
            style = Paint.Style.FILL
        }
    }

    private val smoothPaint by lazy()
    {
        val form = this
        Paint().apply()
        {
            color = ContextCompat.getColor(form, R.color.smooth)
            style = Paint.Style.STROKE
            strokeWidth = 4.0f
            pathEffect = DashPathEffect(floatArrayOf(5f, 10f, 15f, 20f), 0f)
        }
    }

    private val predictionsPaint by lazy()
    {
        val form = this
        Paint().apply()
        {
            color = ContextCompat.getColor(form, R.color.predictions)
            style = Paint.Style.STROKE
            strokeWidth = 8.0f
        }
    }

    private val predictionsCircle by lazy()
    {
        val form = this
        Paint().apply()
        {
            color = ContextCompat.getColor(form, R.color.predictions)
            style = Paint.Style.FILL
        }
    }

    private val titleFont by lazy()
    {
        val form = this
        Paint().apply()
        {
            color = ContextCompat.getColor(form, R.color.black)
            textSize = 30f
        }
    }

    private val axisFont by lazy()
    {
        val form = this
        Paint().apply()
        {
            color = ContextCompat.getColor(form, R.color.black)
            textSize = 14f
        }
    }

    private val textBounds = Rect()

    override fun onCreate(savedInstanceState: Bundle?)
    {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.form_pair)

        val pair = intent.getStringExtra("pair").toString()

        val onUpdate =
        {
            InternetData(this, "http://0v.ru/NeuroInvest/get_pairs_data.php?pair=" + pair)
            {
                result ->

                val pairData = JSONObject(result)

                runOnUiThread()
                {
                    drawGraph(pair, pairData)
                }
            }
        }

        onUpdate()

        refresh.setOnClickListener { onUpdate() }
        close.setOnClickListener { finish() }
    }

    private fun drawGraph(pairName: String, pairData: JSONObject)
    {
        val graphBitmap = Bitmap.createBitmap(graph.width, graph.height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(graphBitmap)

        drawTradeData(canvas, graph.width.toFloat(), graph.height.toFloat(), pairName, pairData)

        graph.setImageBitmap(graphBitmap)
    }

    private fun drawTradeData(canvas: Canvas, width: Float, height: Float, pairName: String, pairData: JSONObject)
    {
        val tradeX  = parseJSONArrayOfIntegers(pairData.getJSONArray("tradeX"))
        val tradeY  = parseJSONArrayOfFloats(pairData.getJSONArray("tradeY"))
        val smoothY = parseJSONArrayOfFloats(pairData.getJSONArray("smoothY"))
        val predictionsX = parseJSONArrayOfIntegers(pairData.optJSONArray("predictionsX"))
        val predictionsY = parseJSONArrayOfFloats(pairData.optJSONArray("predictionsY"))

        val startTime = tradeX.minOrNull() ?: return
        val endRealTime = tradeX.maxOrNull() ?: 0
        val endTime = max(endRealTime, predictionsX.maxOrNull() ?: 0)

        val minValue = min(tradeY.minOrNull() ?: return, predictionsY.minOrNull() ?: Float.MAX_VALUE)
        val maxValue = max(tradeY.maxOrNull() ?: return, predictionsY.maxOrNull() ?: 0f)

        val minDimension = max(width, height)
        val borderPercent = minDimension * 0.03f

        drawTextCentred(canvas, pairName, width / 2, borderPercent * 3, titleFont)

        canvas.drawRect(borderPercent, borderPercent, width - borderPercent, height - borderPercent, borderPaint)

        val valuesRect = RectF(startTime.toFloat(), minValue, endTime.toFloat(), maxValue)
        val canvasRect = RectF(borderPercent * 2, borderPercent * 2, width - borderPercent * 2, height - borderPercent * 2)

        val (xReal, _) = translateValues(endRealTime.toFloat(), 0f, valuesRect, canvasRect)
        canvas.drawLine(xReal, borderPercent, xReal, height - borderPercent, borderPaint)

        drawTrend(canvas, tradeX, tradeY, valuesRect, canvasRect, valuesPaint, valuesCircle)
        drawTrend(canvas, tradeX, smoothY, valuesRect, canvasRect, smoothPaint, null)
        drawTrend(canvas, predictionsX, predictionsY, valuesRect, canvasRect, predictionsPaint, predictionsCircle)

        val xSteps = 4
        val ySteps = 8

        val dateFormat = SimpleDateFormat("dd.MM HH:mm", Locale.getDefault())

        for (step in 0 .. xSteps)
        {
            val date = Date((startTime + (endTime - startTime) * step.toLong() / xSteps) * 1000)

            canvas.drawText(dateFormat.format(date),
                canvasRect.left + canvas.width * step / xSteps,
                canvasRect.bottom - 14, axisFont)
        }

        for (step in 0 .. ySteps)
        {
            canvas.drawText("%.2f".format(minValue + (maxValue - minValue) * step / xSteps),
                canvasRect.left - borderPercent / 2,
                canvasRect.bottom - canvas.height * step / xSteps + borderPercent / 2, axisFont)
        }
    }

    private fun drawTrend(canvas: Canvas, xData: IntArray, yData: FloatArray, valuesRect: RectF, canvasRect: RectF, paint: Paint, circle: Paint?)
    {
        var (lastX, lastY) = translateValues(xData[0].toFloat(), yData[0], valuesRect, canvasRect)

        for (index in 1 until xData.size)
        {
            val (x, y) = translateValues(xData[index].toFloat(), yData[index], valuesRect, canvasRect)
            canvas.drawLine(lastX, lastY, x, y, paint)

            if (circle != null)
            {
                canvas.drawCircle(x, y, 8f, circle)
            }

            lastX = x
            lastY = y
        }
    }

    private fun translateValues(x: Float, y: Float, valuesRect: RectF, canvasRect: RectF): Pair<Float, Float>
    {
        return Pair(              (x - valuesRect.left) / valuesRect.width()  * canvasRect.width()  + canvasRect.left,
            canvasRect.height() - (y - valuesRect.top)  / valuesRect.height() * canvasRect.height() + canvasRect.top)
    }

    private fun parseJSONArrayOfIntegers(array: JSONArray?): IntArray
    {
        if (array == null)
        {
            return IntArray(0)
        }

        val result = IntArray(array.length())

        for (index in 0 until array.length())
        {
            result[index] = array.getInt(index)
        }

        return result
    }

    private fun parseJSONArrayOfFloats(array: JSONArray?): FloatArray
    {
        if (array == null)
        {
            return FloatArray(0)
        }

        val result = FloatArray(array.length())

        for (index in 0 until array.length())
        {
            result[index] = array.getDouble(index).toFloat()
        }

        return result
    }

    private fun drawTextCentred(canvas: Canvas, text: String, x: Float, y: Float, paint: Paint)
    {
        paint.getTextBounds(text, 0, text.length, textBounds)
        canvas.drawText(text, x - textBounds.exactCenterX(), y - textBounds.exactCenterY(), paint)
    }
}