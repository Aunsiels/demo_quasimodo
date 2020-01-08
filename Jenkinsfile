pipeline {
  agent {
    dockerfile {
      filename 'Dockerfile'
    }

  }
  stages {
    stage('Test') {
      steps {
        sh 'python3 example.py || echo 0'
        sh 'ls -la ~/'
        sh 'grep firefox ~/.xsession-errors'
        sh 'PYTHONPATH=$PYTHONPATH:`pwd` pytest --showlocals -v demo --junit-xml test-reports/results.xml || echo 0'
        sh 'cat geckodriver.log'
      }
    }

    stage('Static Tests') {
      steps {
        echo 'Static Tests'
      }
    }

  }
}
