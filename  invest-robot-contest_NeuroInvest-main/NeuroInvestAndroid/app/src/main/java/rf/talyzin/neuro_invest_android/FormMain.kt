package rf.talyzin.neuro_invest_android

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import android.widget.Button
import org.json.JSONArray

class FormMain : AppCompatActivity()
{
    private val buttons by lazy { arrayOf<Button>(
        findViewById(R.id.pair1),
        findViewById(R.id.pair2),
        findViewById(R.id.pair3),
        findViewById(R.id.pair4),
        findViewById(R.id.pair5),
        findViewById(R.id.pair6))}

    override fun onCreate(savedInstanceState: Bundle?)
    {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.form_main)

        InternetData(this, "http://0v.ru/NeuroInvest/get_pairs.php")
        {
            result ->

            if (result.isNotEmpty())
            {
                val pairsData = JSONArray(result)
                val pairsCount = pairsData.length()

                runOnUiThread()
                {
                    for ((index, button) in buttons.withIndex())
                    {
                        if (index < pairsCount)
                        {
                            val pairName = pairsData.getString(index)
                            button.text = pairName
                            button.visibility = View.VISIBLE

                            button.setOnClickListener()
                            {
                                Intent(this, FormPair::class.java).apply()
                                {
                                    putExtra("pair", pairName)
                                    startActivity(this)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}