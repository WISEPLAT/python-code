package rf.talyzin.neuro_invest_android

import android.content.Context
import android.os.Handler
import android.os.Looper
import java.io.*
import java.lang.Exception
import java.net.*
import java.nio.charset.StandardCharsets

internal class InternetData(context: Context, url: String, private val uploadCompleteListener: (answer: String) -> Unit)
{
    private val urlString: String
    private val userAgent: String
    private val timeout: Int

    private var result: String

    init
    {
        urlString = url
        result = ""
        userAgent = context.getString(R.string.app_name)
        timeout = 10000

        execute()
    }

    @Volatile
    private var gotAnswer = false

    private fun execute()
    {
        val internetThread = Thread()
        {
            try
            {
                val chain = StringBuilder()
                try
                {
                    val url = URL(urlString)
                    val connection = url.openConnection() as HttpURLConnection
                    connection.setRequestProperty("User-Agent", userAgent)
                    connection.requestMethod = "GET"
                    connection.readTimeout = timeout
                    connection.connectTimeout = timeout
                    connection.doInput = true

                    connection.connect()

                    val inputStream = connection.inputStream
                    BufferedReader(InputStreamReader(inputStream, StandardCharsets.UTF_8)).use()
                    {
                        bufferedReader ->
                        while (true)
                        {
                            val readLine = bufferedReader.readLine() ?: break
                            chain.append(readLine)
                        }
                        inputStream.close()
                    }
                }
                catch (e: FileNotFoundException)
                {
                    result = ""

                    sendResult()
                    return@Thread
                }
                catch (exception: Exception)
                {
                    exception.printStackTrace()
                }

                result = chain.toString()
            }
            catch (e: RuntimeException)
            {
                e.printStackTrace()
            }

            sendResult()
        }

        internetThread.start()

        Handler(Looper.getMainLooper()).postDelayed(
        {
            if (!gotAnswer)
            {
                sendResult()
            }
        }, (timeout * 3).toLong())

    }

    private fun sendResult()
    {
        if (!gotAnswer)
        {
            gotAnswer = true
            uploadCompleteListener.invoke(result)
        }
    }
}