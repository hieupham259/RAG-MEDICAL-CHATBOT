from flask import Flask, render_template, request,session, redirect,url_for, jsonify
from app.components.retriever import create_qa_chain
from dotenv import load_dotenv
import os


load_dotenv()
HF_TOKEN = os.environ.get("HF_TOKEN")

app = Flask(__name__, template_folder='app/templates')
app.secret_key = os.urandom(24)
load_dotenv()

from markupsafe import Markup
def nl2br(value):
    return Markup(value.replace("\n" , "<br>\n"))

app.jinja_env.filters['nl2br'] = nl2br

@app.route("/" , methods=["GET","POST"])
def index():
    if "messages" not in session:
        session["messages"]=[]

    if request.method=="POST":
        user_input = request.form.get("prompt")

        if user_input:
            messages = session["messages"]
            messages.append({"role" : "user" , "content": user_input})
            session["messages"] = messages

            try:
                qa_chain = create_qa_chain()
                if qa_chain is None:
                    raise Exception("QA chain could not be created (LLM or VectorStore issue)")
                response = qa_chain.invoke({"question" : user_input})
                # print("Response from QA chain :" , response, type(response))
                result = response.content

                messages.append({"role" : "assistant" , "content" : result})
                session["messages"] = messages

            except Exception as e:
                error_msg = f"Error : {str(e)}"
                return render_template("index.html" , messages = session["messages"] , error = error_msg)
            
        return redirect(url_for("index"))
    return render_template("index.html" , messages=session.get("messages" , []))

@app.route("/api/chat", methods=["POST"])
def chat():
    """API endpoint for chat messages"""
    try:
        data = request.get_json()
        user_input = data.get("message")
        
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        
        # Add user message to session
        if "messages" not in session:
            session["messages"] = []
        
        messages = session["messages"]
        messages.append({"role": "user", "content": user_input})
        session["messages"] = messages
        
        # Get AI response
        try:
            qa_chain = create_qa_chain()
            if qa_chain is None:
                raise Exception("QA chain could not be created (LLM or VectorStore issue)")
            
            response = qa_chain.invoke({"question": user_input})
            result = response.content
            
            # Add assistant message to session
            messages.append({"role": "assistant", "content": result})
            session["messages"] = messages
            
            return jsonify({
                "success": True,
                "response": result
            })
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return jsonify({
                "success": False,
                "error": error_msg
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/clear")
def clear():
    session.pop("messages" , None)
    return redirect(url_for("index"))

if __name__=="__main__":
    app.run(host="0.0.0.0" , port=5000 , debug=True , use_reloader = True)


